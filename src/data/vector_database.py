import os
import logging
import time
import pandas as pd
from dotenv import load_dotenv
from qdrant_client import models
from typing import List, Dict, Any
from src.data.zotero_integration import pull_from_zotero

from agno.vectordb.qdrant import Qdrant
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.semantic import SemanticChunking

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class QdrantTools:
    def __init__(self, collection_name: str, qdrant_host: str, qdrant_port: int, embedder: Any = None):
        self.collection_name = collection_name
        self.qdrant_client = Qdrant(host=qdrant_host, port=qdrant_port)
        self.embedder = embedder
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        collections = self.qdrant_client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            logging.info(f"Creating Qdrant collection: {self.collection_name}")
            self.qdrant_client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.embedder.dimensions, distance=models.Distance.COSINE),
            )
        else:
            logging.info(f"Qdrant collection '{self.collection_name}' already exists.")

    def upsert_vectors(self, points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Upserts vectors (embeddings) and their associated payloads into the Qdrant collection.
        Args:
            points: A list of dictionaries, each representing a point to upsert.
                    Each dictionary should have 'vector' (list of floats) and 'payload' (dict).
        """
        qdrant_points = [
            models.PointStruct(
                vector=point["vector"],
                payload=point["payload"]
            )
            for point in points
        ]
        operation_info = self.qdrant_client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=qdrant_points
        )
        logging.info(f"Qdrant upsert operation: {operation_info}")
        return {"status": "success", "operation_info": operation_info.dict()}

def load_database(pdf_directory: str, skip_add=False):
    COLLECTION_NAME = "master_literature_review"

    vector_db = Qdrant(collection=COLLECTION_NAME, url="http://localhost:6333")

    contents_db = PostgresDb(
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
        knowledge_table="knowledge_contents",
    )

    knowledge = Knowledge(
        name="Literature Review Knowledge Base",
        description="A knowledge base for literature review documents.",
        vector_db=vector_db,
        contents_db=contents_db,
        max_results=50
    )

    library = pd.read_csv('/home/mlevi/Work/research-assistant/src/data/zotero_pdf_matches.csv', encoding='windows-1252')
    articles_metadata = pull_from_zotero()

    if not skip_add:
        for i, row in library.iterrows():
            title = row['title']
            pdf_name = row['pdf_name']
            if pdf_name:
                filepath = os.path.join(pdf_directory, pdf_name)
                try:
                    knowledge.add_content(
                        name=title,
                        path=filepath,
                        metadata=articles_metadata[i],
                        reader=PDFReader(
                            name="Semantic Chunking Reader",
                            chunking_strategy=SemanticChunking(similarity_threshold=0.5),
                        ),
                        skip_if_exists=True
                    )
                except Exception as e:
                    logging.error(f"Error on Add Knowledge: {e}")
                    time.sleep(5)
    return knowledge