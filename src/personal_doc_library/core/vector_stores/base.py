#!/usr/bin/env python3
"""
Base abstract class for vector store adapters
Defines the interface that all vector database implementations must follow
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document


class VectorStoreAdapter(ABC):
    """Abstract base class for vector store adapters"""

    def __init__(self, persist_directory: str, embeddings: Any, **kwargs):
        """
        Initialize the vector store adapter

        Args:
            persist_directory: Directory for persisting the vector store
            embeddings: Embeddings function/model to use
            **kwargs: Additional adapter-specific configuration
        """
        self.persist_directory = persist_directory
        self.embeddings = embeddings
        self.config = kwargs

    @abstractmethod
    def initialize(self) -> None:
        """Initialize or load the vector store"""
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store

        Args:
            documents: List of Document objects to add

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with relevance scores

        Args:
            query: Search query text
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of (Document, score) tuples
        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Search query text
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of Document objects
        """
        pass

    @abstractmethod
    def delete(self, filter: Dict[str, Any]) -> None:
        """
        Delete documents matching the filter

        Args:
            filter: Metadata filter for documents to delete
        """
        pass

    @abstractmethod
    def get_collection(self) -> Any:
        """
        Get the underlying collection/client object

        Returns:
            The native collection object for direct operations
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of documents in the vector store

        Returns:
            Total document count
        """
        pass

    @abstractmethod
    def persist(self) -> None:
        """Persist the vector store to disk"""
        pass

    @abstractmethod
    def get_by_filter(
        self,
        filter: Dict[str, Any],
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get documents by filter without similarity search

        Args:
            filter: Metadata filter
            limit: Maximum number of results

        Returns:
            Dictionary with documents and metadata
        """
        pass

    @property
    @abstractmethod
    def vector_store_name(self) -> str:
        """Return the name of the vector store implementation"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(persist_directory='{self.persist_directory}')"
