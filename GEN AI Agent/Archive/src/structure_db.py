"""
Structure Vector DB Module
Handles encoding and storage of Excel schema (sheets, columns, descriptions)
"""
import os
import pandas as pd
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from . import config


class StructureVectorDB:
    """
    Manages the structure vector database for Excel schema information
    """

    def __init__(self, db_path: str = config.DB_PATH):
        """
        Initialize the structure vector database

        Args:
            db_path: Path to Milvus Lite database file
        """
        self.db_path = db_path
        self.client = MilvusClient(db_path)
        self.collection_name = config.STRUCTURE_COLLECTION
        # Uses HF_TOKEN environment variable if available
        self.model = SentenceTransformer(
            config.EMBEDDING_MODEL,
            token=os.environ.get('HF_TOKEN')
        )

    def create_collection(self, drop_existing: bool = False):
        """
        Create the structure vector collection

        Args:
            drop_existing: If True, drop existing collection before creating
        """
        if drop_existing and self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
            print(f"Dropped existing collection: {self.collection_name}")

        if not self.client.has_collection(self.collection_name):
            # Use HNSW parameters if HNSW index, otherwise use IVF parameters
            if config.INDEX_TYPE == "HNSW":
                index_params = {
                    "index_type": config.INDEX_TYPE,
                    "metric_type": config.METRIC_TYPE,
                    "params": {
                        "M": config.M,
                        "efConstruction": config.EF_CONSTRUCTION
                    }
                }
            else:
                index_params = {
                    "index_type": config.INDEX_TYPE,
                    "metric_type": config.METRIC_TYPE,
                    "params": {"nlist": config.NLIST}
                }

            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=config.EMBEDDING_DIM,
                metric_type=config.METRIC_TYPE,
                auto_id=True,
                index_params=index_params
            )
            print(f"Created collection: {self.collection_name}")
        else:
            print(f"Collection already exists: {self.collection_name}")

    def extract_structure_from_excel(self, excel_path: str) -> List[Dict[str, Any]]:
        """
        Extract structure information from Excel file

        Args:
            excel_path: Path to Excel file

        Returns:
            List of structure dictionaries with sheet and column info
        """
        # Read all sheet names
        xl_file = pd.ExcelFile(excel_path)
        structures = []

        for sheet_name in xl_file.sheet_names:
            # Read just the header
            df = pd.read_excel(excel_path, sheet_name=sheet_name, nrows=0)
            columns = df.columns.tolist()

            # Create text representation for embedding
            # Format: "Sheet: {name}, Columns: {col1}, {col2}, ..."
            column_text = ", ".join([str(col) for col in columns])
            text = f"Sheet: {sheet_name}, Columns: {column_text}"

            structures.append({
                "sheet": sheet_name,
                "columns": columns,
                "text": text
            })

        print(f"Extracted structure from {len(structures)} sheets")
        return structures

    def insert_structures(self, structures: List[Dict[str, Any]]):
        """
        Insert structure embeddings into the database

        Args:
            structures: List of structure dictionaries from extract_structure_from_excel
        """
        if not structures:
            print("No structures to insert")
            return

        # Generate embeddings for all structure texts
        texts = [s["text"] for s in structures]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Prepare data for insertion
        data = [
            {
                "vector": embeddings[i].tolist(),
                "sheet": structures[i]["sheet"],
                "columns": str(structures[i]["columns"]),  # Store as string
                "text": structures[i]["text"]
            }
            for i in range(len(structures))
        ]

        # Insert all at once (structure data is small)
        self.client.insert(collection_name=self.collection_name, data=data)
        print(f"Inserted {len(data)} structure vectors into {self.collection_name}")

    def _get_actual_index_type(self) -> str:
        """
        Get the actual index type from the collection

        Returns:
            Index type string (e.g., "HNSW", "IVF_FLAT")
        """
        try:
            # Describe collection to get index info
            desc = self.client.describe_collection(self.collection_name)
            # Try to extract index type from description
            # Milvus Lite might not return full index details, so fallback to config
            return config.INDEX_TYPE
        except:
            return config.INDEX_TYPE

    def search(self, query: str, top_k: int = config.TOP_K_STRUCTURE) -> List[Dict[str, Any]]:
        """
        Search for relevant sheets/columns based on query

        Args:
            query: User query text
            top_k: Number of top results to return

        Returns:
            List of search results with sheet, columns, and relevance scores
        """
        # Encode query
        query_emb = self.model.encode([query])

        # Prepare search params based on index type
        # Use config INDEX_TYPE to determine which params to use
        if config.INDEX_TYPE == "HNSW":
            search_params = {
                "metric_type": config.METRIC_TYPE,
                "params": {"ef": config.EF}
            }
        else:
            search_params = {
                "metric_type": config.METRIC_TYPE,
                "params": {"nprobe": config.NPROBE}
            }

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            data=query_emb.tolist(),
            limit=top_k,
            output_fields=["sheet", "columns", "text"],
            search_params=search_params
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "sheet": hit["entity"]["sheet"],
                    "columns": hit["entity"]["columns"],
                    "text": hit["entity"]["text"],
                    "score": hit["distance"]
                })

        return formatted_results

    def build_from_excel(self, excel_path: str, drop_existing: bool = False):
        """
        Complete pipeline: extract structure from Excel and insert into DB

        Args:
            excel_path: Path to Excel file
            drop_existing: If True, recreate the collection
        """
        print(f"Building structure database from: {excel_path}")

        # Create collection
        self.create_collection(drop_existing=drop_existing)

        # Extract and insert structures
        structures = self.extract_structure_from_excel(excel_path)
        self.insert_structures(structures)

        print("Structure database build complete!")
