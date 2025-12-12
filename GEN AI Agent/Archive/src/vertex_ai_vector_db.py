"""
Vertex AI Vector Search Integration
Stores vectors in GCS and queries remotely - no local download needed
"""
from google.cloud import aiplatform
from google.cloud import storage
from sentence_transformers import SentenceTransformer
import pandas as pd
import json
import os
from typing import List, Dict, Any


class VertexAIVectorDB:
    """
    Vector database using Vertex AI Vector Search (Matching Engine)
    Data is stored in GCS and queried remotely
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        bucket_name: str = "edeliverydata",
        index_name: str = "edelivery_index"
    ):
        self.project_id = project_id
        self.location = location
        self.bucket_name = bucket_name
        self.index_name = index_name

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        # Initialize embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def build_from_gcs_excel(
        self,
        excel_file_path: str = "edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx"
    ):
        """
        Build vector index from Excel file in GCS
        Data stays in GCS, no local download needed for queries

        Args:
            excel_file_path: Path to Excel file in GCS bucket
        """
        print(f"Building Vertex AI Vector Search index from gs://{self.bucket_name}/{excel_file_path}")

        # Step 1: Read Excel from GCS
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(excel_file_path)

        import io
        file_content = blob.download_as_bytes()
        all_sheets = pd.read_excel(io.BytesIO(file_content), sheet_name=None)

        # Step 2: Extract and embed data
        embeddings_data = []

        for sheet_name, df in all_sheets.items():
            # Structure chunk
            columns = df.columns.tolist()
            column_text = ", ".join([str(col) for col in columns])
            structure_text = f"Sheet: {sheet_name}, Columns: {column_text}"
            structure_embedding = self.model.encode(structure_text).tolist()

            embeddings_data.append({
                "id": f"structure_{sheet_name}",
                "embedding": structure_embedding,
                "metadata": {
                    "sheet": sheet_name,
                    "type": "structure",
                    "text": structure_text
                }
            })

            # Content chunks
            for idx, row in df.iterrows():
                row_text = " | ".join([str(val) for val in row.values[:5]])
                if row_text.strip():
                    content_embedding = self.model.encode(row_text).tolist()

                    embeddings_data.append({
                        "id": f"content_{sheet_name}_{idx}",
                        "embedding": content_embedding,
                        "metadata": {
                            "sheet": sheet_name,
                            "type": "content",
                            "text": row_text
                        }
                    })

        # Step 3: Upload embeddings to GCS in JSONL format
        embeddings_file = f"embeddings_{self.index_name}.jsonl"
        local_temp = f"/tmp/{embeddings_file}"

        with open(local_temp, 'w') as f:
            for item in embeddings_data:
                f.write(json.dumps(item) + "\n")

        # Upload to GCS
        blob = bucket.blob(f"vector_embeddings/{embeddings_file}")
        blob.upload_from_filename(local_temp)

        gcs_uri = f"gs://{self.bucket_name}/vector_embeddings/{embeddings_file}"
        print(f"✓ Embeddings uploaded to {gcs_uri}")

        # Step 4: Create Vertex AI Vector Search Index
        print("Creating Vertex AI Vector Search index...")

        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=self.index_name,
            contents_delta_uri=gcs_uri,
            dimensions=384,  # all-MiniLM-L6-v2 dimension
            approximate_neighbors_count=10,
            distance_measure_type="COSINE_DISTANCE"
        )

        print(f"✓ Index created: {index.resource_name}")
        return index

    def query(self, query_text: str, top_k: int = 10):
        """
        Query the vector database remotely (no download needed)

        Args:
            query_text: User query
            top_k: Number of results

        Returns:
            List of results
        """
        # Generate query embedding
        query_embedding = self.model.encode(query_text).tolist()

        # Get deployed index endpoint
        # Note: You need to deploy the index first
        endpoints = aiplatform.MatchingEngineIndexEndpoint.list(
            filter=f'display_name="{self.index_name}_endpoint"'
        )

        if not endpoints:
            raise ValueError("Index endpoint not found. Please deploy the index first.")

        endpoint = endpoints[0]

        # Query
        response = endpoint.find_neighbors(
            deployed_index_id=self.index_name,
            queries=[query_embedding],
            num_neighbors=top_k
        )

        return response
