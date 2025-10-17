"""
Content Vector DB Module
Handles encoding and storage of Excel row-level content
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from . import config


class ContentVectorDB:
    """
    Manages the content vector database for Excel row-level data
    """

    def __init__(self, db_path: str = config.DB_PATH):
        """
        Initialize the content vector database

        Args:
            db_path: Path to Milvus Lite database file
        """
        self.db_path = db_path
        self.client = MilvusClient(db_path)
        self.collection_name = config.CONTENT_COLLECTION
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)

    def create_collection(self, drop_existing: bool = False):
        """
        Create the content vector collection

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

    def extract_content_from_excel(self, excel_path: str, max_columns: int = 5) -> pd.DataFrame:
        """
        Extract row-level content from Excel file

        Args:
            excel_path: Path to Excel file
            max_columns: Maximum number of columns to concatenate (default: 5)

        Returns:
            DataFrame with columns: sheet, text
        """
        all_sheets = pd.read_excel(excel_path, sheet_name=None)

        dfs = []
        for sheet_name, df in all_sheets.items():
            # Concatenate first N columns for richer context
            num_cols = min(len(df.columns), max_columns)

            # Combine multiple columns into text with column names as context
            text_parts = []
            for col in df.columns[:num_cols]:
                # Format: "ColumnName: value"
                text_parts.append(df[col].astype(str))

            # Join with " | " separator for clarity
            combined_text = text_parts[0].str.cat(text_parts[1:], sep=" | ", na_rep="")

            temp = pd.DataFrame({
                "sheet": sheet_name,
                "text": combined_text
            })
            dfs.append(temp)

        full_df = pd.concat(dfs, ignore_index=True)
        print(f"Extracted {len(full_df)} rows across {len(all_sheets)} sheets")
        print(f"Using up to {max_columns} columns per row for richer context")
        return full_df

    def insert_content_batched(self, content_df: pd.DataFrame, batch_size: int = config.BATCH_SIZE):
        """
        Insert content embeddings into database in batches

        Args:
            content_df: DataFrame with 'sheet' and 'text' columns
            batch_size: Number of rows to process per batch
        """
        total_rows = len(content_df)
        print(f"Starting batch insertion of {total_rows} rows...")

        # Generate embeddings for all content (this may take a while)
        print("Generating embeddings...")
        embeddings = self.model.encode(
            content_df["text"].tolist(),
            show_progress_bar=True,
            batch_size=32
        )

        print(f"Embeddings generated. Inserting into database...")

        # Insert in batches
        for i in range(0, total_rows, batch_size):
            batch_end = min(i + batch_size, total_rows)

            # Prepare batch data
            batch_data = [
                {
                    "vector": embeddings[j].tolist(),
                    "sheet": content_df["sheet"].iloc[j],
                    "text": content_df["text"].iloc[j]
                }
                for j in range(i, batch_end)
            ]

            # Insert batch
            self.client.insert(collection_name=self.collection_name, data=batch_data)

            # Progress update every 5000 rows
            if (i + batch_size) % 5000 == 0 or batch_end == total_rows:
                print(f"Inserted {batch_end}/{total_rows} rows...")

        print(f"Successfully inserted all {total_rows} rows into {self.collection_name}")

    def search(
        self,
        query: str,
        top_k: int = config.TOP_K_CONTENT,
        sheet_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant content based on query

        Args:
            query: User query text
            top_k: Number of top results to return
            sheet_filter: Optional list of sheet names to filter by

        Returns:
            List of search results with sheet, text, and relevance scores
        """
        # Encode query
        query_emb = self.model.encode([query])

        # Prepare search parameters based on index type
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

        # Build filter expression if sheet filter provided
        filter_expr = None
        if sheet_filter:
            # Milvus filter expression for matching sheets
            sheet_conditions = [f"sheet == '{sheet}'" for sheet in sheet_filter]
            filter_expr = " or ".join(sheet_conditions)

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            data=query_emb.tolist(),
            limit=top_k,
            output_fields=["sheet", "text"],
            search_params=search_params,
            filter=filter_expr
        )

        # Format results with deduplication
        formatted_results = []
        seen_texts = set()

        for hits in results:
            for hit in hits:
                text = hit["entity"]["text"]
                # Skip near-duplicates (exact match)
                if text in seen_texts:
                    continue

                seen_texts.add(text)
                formatted_results.append({
                    "sheet": hit["entity"]["sheet"],
                    "text": text,
                    "score": hit["distance"]
                })

        return formatted_results

    def build_from_excel(self, excel_path: str, drop_existing: bool = False):
        """
        Complete pipeline: extract content from Excel and insert into DB

        Args:
            excel_path: Path to Excel file
            drop_existing: If True, recreate the collection
        """
        print(f"Building content database from: {excel_path}")

        # Create collection
        self.create_collection(drop_existing=drop_existing)

        # Extract and insert content
        content_df = self.extract_content_from_excel(excel_path)
        self.insert_content_batched(content_df)

        print("Content database build complete!")
