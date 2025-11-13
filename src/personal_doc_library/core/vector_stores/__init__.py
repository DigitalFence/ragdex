#!/usr/bin/env python3
"""
Vector store adapters for ragdex
Provides abstraction layer for multiple vector database backends
"""

from .base import VectorStoreAdapter
from .chroma_adapter import ChromaDBAdapter
from .factory import VectorStoreFactory

# Try to import optional adapters
try:
    from .qdrant_adapter import QdrantAdapter
    __all__ = [
        'VectorStoreAdapter',
        'ChromaDBAdapter',
        'QdrantAdapter',
        'VectorStoreFactory'
    ]
except ImportError:
    __all__ = [
        'VectorStoreAdapter',
        'ChromaDBAdapter',
        'VectorStoreFactory'
    ]

# Version info
__version__ = '1.0.0'
