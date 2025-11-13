#!/usr/bin/env python3
"""
Factory for creating vector store adapters based on configuration
"""

import os
import logging
from typing import Any, Optional, Dict

from .base import VectorStoreAdapter
from .chroma_adapter import ChromaDBAdapter

logger = logging.getLogger(__name__)


class VectorStoreFactory:
    """Factory for creating vector store adapters"""

    # Registry of available vector stores
    _registry = {
        'chromadb': ChromaDBAdapter,
        'chroma': ChromaDBAdapter,
    }

    @classmethod
    def register_adapter(cls, name: str, adapter_class: type):
        """
        Register a new vector store adapter

        Args:
            name: Name identifier for the adapter
            adapter_class: The adapter class (must inherit from VectorStoreAdapter)
        """
        if not issubclass(adapter_class, VectorStoreAdapter):
            raise ValueError(f"Adapter class must inherit from VectorStoreAdapter")

        cls._registry[name.lower()] = adapter_class
        logger.info(f"Registered vector store adapter: {name}")

    @classmethod
    def create(
        cls,
        vector_store_type: str,
        persist_directory: str,
        embeddings: Any,
        **kwargs
    ) -> VectorStoreAdapter:
        """
        Create a vector store adapter

        Args:
            vector_store_type: Type of vector store ('chromadb', 'qdrant', etc.)
            persist_directory: Directory for persistence
            embeddings: Embeddings model/function
            **kwargs: Additional configuration for the specific adapter

        Returns:
            Initialized VectorStoreAdapter instance

        Raises:
            ValueError: If vector_store_type is not supported
        """
        vector_store_type_lower = vector_store_type.lower()

        if vector_store_type_lower not in cls._registry:
            available = ', '.join(cls._registry.keys())
            raise ValueError(
                f"Unsupported vector store type: '{vector_store_type}'. "
                f"Available types: {available}"
            )

        adapter_class = cls._registry[vector_store_type_lower]

        try:
            logger.info(f"Creating {vector_store_type} adapter")
            adapter = adapter_class(persist_directory, embeddings, **kwargs)
            adapter.initialize()
            return adapter
        except ImportError as e:
            logger.error(f"Failed to import {vector_store_type} dependencies: {e}")
            raise ImportError(
                f"Vector store '{vector_store_type}' requires additional dependencies. "
                f"Install them with: pip install {cls._get_install_command(vector_store_type_lower)}"
            ) from e
        except Exception as e:
            logger.error(f"Error creating {vector_store_type} adapter: {e}")
            raise

    @classmethod
    def create_from_config(
        cls,
        config: Dict[str, Any],
        persist_directory: str,
        embeddings: Any
    ) -> VectorStoreAdapter:
        """
        Create a vector store adapter from configuration dictionary

        Args:
            config: Configuration dictionary with 'type' and other settings
            persist_directory: Directory for persistence
            embeddings: Embeddings model/function

        Returns:
            Initialized VectorStoreAdapter instance
        """
        vector_store_type = config.get('type', 'chromadb')

        # Extract adapter-specific config (everything except 'type')
        adapter_config = {k: v for k, v in config.items() if k != 'type'}

        return cls.create(vector_store_type, persist_directory, embeddings, **adapter_config)

    @classmethod
    def create_from_env(
        cls,
        persist_directory: str,
        embeddings: Any,
        env_prefix: str = "RAGDEX_VECTOR_STORE"
    ) -> VectorStoreAdapter:
        """
        Create a vector store adapter from environment variables

        Environment variables:
            {PREFIX}_TYPE: Type of vector store (default: 'chromadb')
            {PREFIX}_COLLECTION_NAME: Collection name
            {PREFIX}_MODE: Mode for QDrant ('local', 'memory', 'remote')
            {PREFIX}_URL: URL for remote vector store
            {PREFIX}_API_KEY: API key for authentication
            {PREFIX}_HOST: Host for remote vector store
            {PREFIX}_PORT: Port for remote vector store
            ... (adapter-specific variables)

        Args:
            persist_directory: Directory for persistence
            embeddings: Embeddings model/function
            env_prefix: Prefix for environment variables

        Returns:
            Initialized VectorStoreAdapter instance
        """
        vector_store_type = os.getenv(f"{env_prefix}_TYPE", "chromadb")

        # Build config from environment variables
        config = {}
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(env_prefix)}

        for key, value in env_vars.items():
            # Remove prefix and convert to lowercase
            config_key = key[len(env_prefix) + 1:].lower()
            if config_key != 'type':
                # Try to parse as int or bool
                if value.lower() in ('true', 'false'):
                    config[config_key] = value.lower() == 'true'
                elif value.isdigit():
                    config[config_key] = int(value)
                else:
                    config[config_key] = value

        logger.info(f"Creating vector store from environment: type={vector_store_type}")
        return cls.create(vector_store_type, persist_directory, embeddings, **config)

    @classmethod
    def _get_install_command(cls, vector_store_type: str) -> str:
        """Get installation command for a vector store type"""
        install_commands = {
            'qdrant': 'qdrant-client',
            'pinecone': 'pinecone-client',
            'weaviate': 'weaviate-client',
            'milvus': 'pymilvus',
        }
        return install_commands.get(vector_store_type, f'{vector_store_type}-client')

    @classmethod
    def list_available(cls) -> list:
        """List all available (registered) vector store types"""
        return list(cls._registry.keys())


# Auto-register QDrant adapter if available
try:
    from .qdrant_adapter import QdrantAdapter
    VectorStoreFactory.register_adapter('qdrant', QdrantAdapter)
except ImportError:
    logger.debug("QDrant adapter not available (qdrant-client not installed)")


# Optional: Auto-register other adapters when they're created
# Example:
# try:
#     from .pinecone_adapter import PineconeAdapter
#     VectorStoreFactory.register_adapter('pinecone', PineconeAdapter)
# except ImportError:
#     logger.debug("Pinecone adapter not available")
