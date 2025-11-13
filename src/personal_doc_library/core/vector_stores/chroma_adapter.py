#!/usr/bin/env python3
"""
ChromaDB adapter implementation
Wraps LangChain's Chroma vector store
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from .base import VectorStoreAdapter

logger = logging.getLogger(__name__)


class ChromaDBAdapter(VectorStoreAdapter):
    """ChromaDB implementation of the VectorStoreAdapter"""

    def __init__(self, persist_directory: str, embeddings: Any, **kwargs):
        """
        Initialize ChromaDB adapter

        Args:
            persist_directory: Directory for ChromaDB persistence
            embeddings: Embeddings function/model
            **kwargs: Additional ChromaDB-specific configuration
                - collection_name: Name of the ChromaDB collection (default: "ragdex")
                - collection_metadata: Metadata for the collection
        """
        super().__init__(persist_directory, embeddings, **kwargs)
        self._vectorstore = None
        self.collection_name = kwargs.get('collection_name', 'ragdex')
        self.collection_metadata = kwargs.get('collection_metadata', None)

    def initialize(self) -> None:
        """Initialize or load ChromaDB vector store"""
        try:
            if os.path.exists(self.persist_directory) and os.path.exists(
                os.path.join(self.persist_directory, "chroma.sqlite3")
            ):
                logger.info(f"Loading existing ChromaDB from {self.persist_directory}")
                self._vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
            else:
                logger.info(f"Creating new ChromaDB at {self.persist_directory}")
                os.makedirs(self.persist_directory, exist_ok=True)
                self._vectorstore = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name,
                    collection_metadata=self.collection_metadata
                )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to ChromaDB"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            ids = self._vectorstore.add_documents(documents)
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
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
                search_kwargs["filter"] = filter

            results = self._vectorstore.similarity_search_with_score(query, **search_kwargs)
            return results
        except Exception as e:
            logger.error(f"Error in ChromaDB similarity search: {e}")
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
                search_kwargs["filter"] = filter

            results = self._vectorstore.similarity_search(query, **search_kwargs)
            return results
        except Exception as e:
            logger.error(f"Error in ChromaDB similarity search: {e}")
            raise

    def delete(self, filter: Dict[str, Any]) -> None:
        """Delete documents matching the filter"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            collection = self._vectorstore._collection
            collection.delete(where=filter)
            logger.info(f"Deleted documents matching filter: {filter}")
        except Exception as e:
            logger.error(f"Error deleting documents from ChromaDB: {e}")
            raise

    def get_collection(self) -> Any:
        """Get the underlying ChromaDB collection"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        return self._vectorstore._collection

    def count(self) -> int:
        """Get total document count"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            collection = self._vectorstore._collection
            return collection.count() or 0
        except Exception as e:
            logger.error(f"Error getting count from ChromaDB: {e}")
            return 0

    def persist(self) -> None:
        """Persist ChromaDB to disk"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            self._vectorstore.persist()
            logger.debug("ChromaDB persisted successfully")
        except Exception as e:
            logger.error(f"Error persisting ChromaDB: {e}")
            raise

    def get_by_filter(
        self,
        filter: Dict[str, Any],
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get documents by filter without similarity search"""
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            collection = self._vectorstore._collection
            kwargs = {"where": filter, "include": ["documents", "metadatas", "ids"]}
            if limit:
                kwargs["limit"] = limit

            results = collection.get(**kwargs)
            return results
        except Exception as e:
            logger.error(f"Error getting documents by filter from ChromaDB: {e}")
            raise

    @property
    def vector_store_name(self) -> str:
        """Return the vector store name"""
        return "ChromaDB"

    def get_native_vectorstore(self) -> Chroma:
        """
        Get the native LangChain Chroma vectorstore object

        This is provided for backward compatibility with existing code
        that directly accesses the Chroma object.

        Returns:
            The underlying Chroma vectorstore
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self._vectorstore
