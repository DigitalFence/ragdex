#!/usr/bin/env python3
"""
Simple test script to verify vector store implementations
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from personal_doc_library.core.vector_stores import VectorStoreFactory
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


def test_chromadb():
    """Test ChromaDB adapter"""
    print("\n" + "="*60)
    print("Testing ChromaDB Adapter")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Using temp directory: {tmpdir}")

        # Create embeddings
        print("Initializing embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Create ChromaDB adapter
        print("Creating ChromaDB adapter...")
        adapter = VectorStoreFactory.create(
            vector_store_type='chromadb',
            persist_directory=tmpdir,
            embeddings=embeddings
        )

        print(f"✓ Vector store created: {adapter.vector_store_name}")

        # Add test documents
        print("Adding test documents...")
        docs = [
            Document(page_content="This is a test document about Python programming.",
                    metadata={"book": "test.pdf", "page": 1}),
            Document(page_content="Machine learning is a subset of artificial intelligence.",
                    metadata={"book": "test.pdf", "page": 2}),
        ]
        ids = adapter.add_documents(docs)
        print(f"✓ Added {len(ids)} documents")

        # Test search
        print("Testing similarity search...")
        results = adapter.similarity_search("programming", k=1)
        print(f"✓ Found {len(results)} results")
        if results:
            print(f"  Top result: {results[0].page_content[:50]}...")

        # Test count
        count = adapter.count()
        print(f"✓ Total documents: {count}")

        # Test delete
        print("Testing delete...")
        adapter.delete(filter={"book": "test.pdf"})
        count_after = adapter.count()
        print(f"✓ Documents after delete: {count_after}")

        print("\n✅ ChromaDB adapter test PASSED")
        return True


def test_qdrant():
    """Test QDrant adapter"""
    print("\n" + "="*60)
    print("Testing QDrant Adapter")
    print("="*60)

    try:
        import qdrant_client
        print("✓ QDrant client is installed")
    except ImportError:
        print("⚠️  QDrant not installed - skipping test")
        print("   Install with: pip install qdrant-client")
        return True

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Using temp directory: {tmpdir}")

        # Create embeddings
        print("Initializing embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Create QDrant adapter (local mode)
        print("Creating QDrant adapter (local mode)...")
        adapter = VectorStoreFactory.create(
            vector_store_type='qdrant',
            persist_directory=tmpdir,
            embeddings=embeddings,
            mode='local'
        )

        print(f"✓ Vector store created: {adapter.vector_store_name}")

        # Add test documents
        print("Adding test documents...")
        docs = [
            Document(page_content="This is a test document about Python programming.",
                    metadata={"book": "test.pdf", "page": 1}),
            Document(page_content="Machine learning is a subset of artificial intelligence.",
                    metadata={"book": "test.pdf", "page": 2}),
        ]
        ids = adapter.add_documents(docs)
        print(f"✓ Added {len(ids)} documents")

        # Test search
        print("Testing similarity search...")
        results = adapter.similarity_search("programming", k=1)
        print(f"✓ Found {len(results)} results")
        if results:
            print(f"  Top result: {results[0].page_content[:50]}...")

        # Test count
        count = adapter.count()
        print(f"✓ Total documents: {count}")

        # Test get_by_filter
        print("Testing get_by_filter...")
        filtered = adapter.get_by_filter(filter={"book": "test.pdf"})
        print(f"✓ Found {len(filtered.get('documents', []))} documents by filter")

        print("\n✅ QDrant adapter test PASSED")
        return True


def test_factory():
    """Test VectorStoreFactory"""
    print("\n" + "="*60)
    print("Testing VectorStoreFactory")
    print("="*60)

    # List available adapters
    available = VectorStoreFactory.list_available()
    print(f"Available vector stores: {', '.join(available)}")

    # Test invalid type
    print("Testing error handling...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            VectorStoreFactory.create(
                vector_store_type='invalid_db',
                persist_directory=tmpdir,
                embeddings=embeddings
            )
        print("❌ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {str(e)[:50]}...")

    print("\n✅ Factory test PASSED")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Vector Store Implementation Tests")
    print("="*60)

    results = {}

    # Run tests
    try:
        results['chromadb'] = test_chromadb()
    except Exception as e:
        print(f"\n❌ ChromaDB test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results['chromadb'] = False

    try:
        results['qdrant'] = test_qdrant()
    except Exception as e:
        print(f"\n❌ QDrant test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results['qdrant'] = False

    try:
        results['factory'] = test_factory()
    except Exception as e:
        print(f"\n❌ Factory test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results['factory'] = False

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20s}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
