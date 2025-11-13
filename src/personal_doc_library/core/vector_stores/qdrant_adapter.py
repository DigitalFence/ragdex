#!/usr/bin/env python3
"""
QDrant adapter implementation
Supports local persistent storage, in-memory, and remote QDrant instances
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document

try:
    from langchain_community.vectorstores import Qdrant
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    Qdrant = None
    QdrantClient = None

from .base import VectorStoreAdapter

logger = logging.getLogger(__name__)


class QdrantAdapter(VectorStoreAdapter):
    """QDrant implementation of the VectorStoreAdapter"""

    def __init__(self, persist_directory: str, embeddings: Any, **kwargs):
        """
        Initialize QDrant adapter

        Args:
            persist_directory: Directory for QDrant persistence (for local mode)
            embeddings: Embeddings function/model
            **kwargs: Additional QDrant-specific configuration
                - collection_name: Name of the QDrant collection (default: "ragdex")
                - mode: 'local' (persistent), 'memory', or 'remote' (default: 'local')
                - url: QDrant server URL (for remote mode)
                - api_key: API key for authentication (for remote mode)
                - host: QDrant host (alternative to url)
                - port: QDrant port (default: 6333)
                - grpc_port: gRPC port (default: 6334)
                - prefer_grpc: Whether to prefer gRPC (default: False)
                - distance: Distance metric ('COSINE', 'EUCLID', 'DOT', default: 'COSINE')
                - vector_size: Size of embedding vectors (auto-detected if not provided)
        """
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "QDrant is not installed. Install it with: pip install qdrant-client"
            )

        super().__init__(persist_directory, embeddings, **kwargs)
        self._vectorstore = None
        self._client = None
        self.collection_name = kwargs.get('collection_name', 'ragdex')
        self.mode = kwargs.get('mode', 'local')
        self.url = kwargs.get('url', None)
        self.api_key = kwargs.get('api_key', None)
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 6333)
        self.grpc_port = kwargs.get('grpc_port', 6334)
        self.prefer_grpc = kwargs.get('prefer_grpc', False)
        self.distance_metric = kwargs.get('distance', 'COSINE')
        self.vector_size = kwargs.get('vector_size', None)

    def _get_distance(self) -> Any:
        """Get QDrant distance metric"""
        distance_map = {
            'COSINE': Distance.COSINE,
            'EUCLID': Distance.EUCLID,
            'DOT': Distance.DOT
        }
        return distance_map.get(self.distance_metric.upper(), Distance.COSINE)

    def _create_client(self) -> QdrantClient:
        """Create QDrant client based on mode"""
        if self.mode == 'local':
            # Persistent local storage
            os.makedirs(self.persist_directory, exist_ok=True)
            logger.info(f"Creating local QDrant client at {self.persist_directory}")
            return QdrantClient(path=self.persist_directory)
        elif self.mode == 'memory':
            # In-memory mode (not persistent)
            logger.info("Creating in-memory QDrant client")
            return QdrantClient(location=":memory:")
        elif self.mode == 'remote':
            # Remote QDrant server
            if self.url:
                logger.info(f"Connecting to remote QDrant at {self.url}")
                return QdrantClient(url=self.url, api_key=self.api_key, prefer_grpc=self.prefer_grpc)
            else:
                logger.info(f"Connecting to remote QDrant at {self.host}:{self.port}")
                return QdrantClient(
                    host=self.host,
                    port=self.port,
                    grpc_port=self.grpc_port,
                    api_key=self.api_key,
                    prefer_grpc=self.prefer_grpc
                )
        else:
            raise ValueError(f"Invalid QDrant mode: {self.mode}. Must be 'local', 'memory', or 'remote'")

    def _detect_vector_size(self) -> int:
        """Detect vector size from embeddings model"""
        try:
            # Try to get vector size from embeddings
            if hasattr(self.embeddings, 'client'):
                # HuggingFace embeddings
                if hasattr(self.embeddings.client, 'get_sentence_embedding_dimension'):
                    return self.embeddings.client.get_sentence_embedding_dimension()

            # Fallback: create a test embedding
            test_embedding = self.embeddings.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Error detecting vector size: {e}")
            # Default to common embedding size
            return 768

    def initialize(self) -> None:
        """Initialize or load QDrant vector store"""
        try:
            # Create QDrant client
            self._client = self._create_client()

            # Detect vector size if not provided
            if self.vector_size is None:
                self.vector_size = self._detect_vector_size()
                logger.info(f"Detected vector size: {self.vector_size}")

            # Check if collection exists
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating new QDrant collection: {self.collection_name}")
                # Create collection with vector configuration
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=self._get_distance()
                    )
                )
            else:
                logger.info(f"Using existing QDrant collection: {self.collection_name}")

            # Create LangChain Qdrant vectorstore
            self._vectorstore = Qdrant(
                client=self._client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )

            logger.info("QDrant initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing QDrant: {e}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to QDrant"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            ids = self._vectorstore.add_documents(documents)
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to QDrant: {e}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents with scores"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            search_kwargs = {"k": k}
            if filter:
                # Convert filter to QDrant format
                search_kwargs["filter"] = self._convert_filter(filter)

            results = self._vectorstore.similarity_search_with_score(query, **search_kwargs)
            return results
        except Exception as e:
            logger.error(f"Error in QDrant similarity search: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Search for similar documents"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            search_kwargs = {"k": k}
            if filter:
                search_kwargs["filter"] = self._convert_filter(filter)

            results = self._vectorstore.similarity_search(query, **search_kwargs)
            return results
        except Exception as e:
            logger.error(f"Error in QDrant similarity search: {e}")
            raise

    def _convert_filter(self, filter_dict: Dict[str, Any]) -> Filter:
        """
        Convert simple filter dict to QDrant Filter format

        Supports:
        - Simple key-value: {"book": "example.pdf"} -> FieldCondition match
        - Nested $and, $or operators (ChromaDB style)
        """
        if not filter_dict:
            return None

        conditions = []

        for key, value in filter_dict.items():
            if key == "$and":
                # Handle $and operator
                sub_conditions = [self._convert_filter(f) for f in value]
                return Filter(must=sub_conditions)
            elif key == "$or":
                # Handle $or operator
                sub_conditions = [self._convert_filter(f) for f in value]
                return Filter(should=sub_conditions)
            elif isinstance(value, dict):
                # Handle nested operators like {"$eq": "value"}
                if "$eq" in value:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value["$eq"])))
                else:
                    # Treat as nested filter
                    conditions.append(self._convert_filter({key: v for k, v in value.items()}))
            else:
                # Simple key-value match
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

        if len(conditions) == 1:
            return Filter(must=[conditions[0]])
        elif len(conditions) > 1:
            return Filter(must=conditions)

        return None

    def delete(self, filter: Dict[str, Any]) -> None:
        """Delete documents matching the filter"""
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Convert filter to QDrant format
            qdrant_filter = self._convert_filter(filter)

            # Delete using QDrant client
            self._client.delete(
                collection_name=self.collection_name,
                points_selector=qdrant_filter
            )
            logger.info(f"Deleted documents matching filter: {filter}")
        except Exception as e:
            logger.error(f"Error deleting documents from QDrant: {e}")
            raise

    def get_collection(self) -> Any:
        """Get the underlying QDrant client"""
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        return self._client

    def count(self) -> int:
        """Get total document count"""
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            collection_info = self._client.get_collection(self.collection_name)
            return collection_info.points_count or 0
        except Exception as e:
            logger.error(f"Error getting count from QDrant: {e}")
            return 0

    def persist(self) -> None:
        """
        Persist QDrant to disk

        Note: For local mode, QDrant persists automatically.
        This is a no-op for compatibility with the interface.
        """
        if self.mode == 'local':
            logger.debug("QDrant local mode persists automatically")
        else:
            logger.debug("QDrant persist() called (no-op for non-local modes)")

    def get_by_filter(
        self,
        filter: Dict[str, Any],
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get documents by filter without similarity search"""
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Convert filter to QDrant format
            qdrant_filter = self._convert_filter(filter)

            # Scroll through results
            results = self._client.scroll(
                collection_name=self.collection_name,
                scroll_filter=qdrant_filter,
                limit=limit or 100,
                with_payload=True,
                with_vectors=False
            )

            # Convert to ChromaDB-like format for compatibility
            points, _ = results

            documents = []
            metadatas = []
            ids = []

            for point in points:
                # Extract document content and metadata
                payload = point.payload
                if 'page_content' in payload:
                    documents.append(payload['page_content'])
                    # Remove page_content from metadata
                    metadata = {k: v for k, v in payload.items() if k != 'page_content'}
                    metadatas.append(metadata)
                    ids.append(str(point.id))

            return {
                'documents': documents,
                'metadatas': metadatas,
                'ids': ids
            }
        except Exception as e:
            logger.error(f"Error getting documents by filter from QDrant: {e}")
            raise

    @property
    def vector_store_name(self) -> str:
        """Return the vector store name"""
        return f"QDrant ({self.mode})"

    def get_native_vectorstore(self) -> Any:
        """
        Get the native LangChain Qdrant vectorstore object

        Returns:
            The underlying Qdrant vectorstore
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self._vectorstore
