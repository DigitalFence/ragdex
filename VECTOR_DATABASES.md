# Vector Database Configuration Guide

Ragdex now supports multiple vector database backends, allowing you to choose the best solution for your needs. This guide explains how to configure and use different vector databases.

## Supported Vector Databases

### 1. ChromaDB (Default)
- **Type**: Embedded, SQLite-backed vector database
- **Best for**: Local deployments, single-user setups, ease of use
- **Pros**: No additional setup, automatic persistence, lightweight
- **Cons**: Limited to local use, single-process access

### 2. QDrant
- **Type**: High-performance vector database with multiple deployment modes
- **Best for**: Scalable deployments, distributed systems, production use
- **Pros**: Fast search, supports remote deployment, advanced filtering
- **Cons**: Requires additional installation

## Installation

### ChromaDB (Included by default)
ChromaDB is included in the base installation - no additional steps needed!

### QDrant
Install QDrant support with:

```bash
# Using pip
pip install ragdex[qdrant]

# Or install QDrant client directly
pip install qdrant-client

# Using uv (recommended)
uv pip install ragdex[qdrant]
```

For all vector store backends:
```bash
pip install ragdex[all-vector-stores]
```

## Configuration

Vector database configuration is done via environment variables.

### Basic Configuration

Set the vector store type:

```bash
export RAGDEX_VECTOR_STORE_TYPE=chromadb  # or 'qdrant'
```

### ChromaDB Configuration

ChromaDB works out of the box with default settings. Optional configuration:

```bash
# Set collection name (default: 'ragdex')
export RAGDEX_VECTOR_STORE_COLLECTION_NAME=my_collection

# Data directory is set via existing environment variable
export PERSONAL_LIBRARY_DB_PATH=/path/to/database
```

**Example - Using ChromaDB (default):**
```bash
# No configuration needed - just run ragdex!
ragdex-mcp
```

### QDrant Configuration

QDrant supports three deployment modes:

#### Mode 1: Local Persistent Storage (Recommended)

Store vectors locally with automatic persistence:

```bash
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=local
export RAGDEX_VECTOR_STORE_COLLECTION_NAME=my_docs
export PERSONAL_LIBRARY_DB_PATH=/path/to/qdrant/storage
```

**Example:**
```bash
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=local
ragdex-mcp
```

#### Mode 2: In-Memory Mode

Fast performance, no persistence (good for testing):

```bash
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=memory
```

**Warning**: Data will be lost when the process stops!

#### Mode 3: Remote QDrant Server

Connect to a remote QDrant instance:

```bash
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=remote
export RAGDEX_VECTOR_STORE_URL=http://localhost:6333
# Or specify host/port separately
export RAGDEX_VECTOR_STORE_HOST=localhost
export RAGDEX_VECTOR_STORE_PORT=6333

# Optional: Authentication
export RAGDEX_VECTOR_STORE_API_KEY=your_api_key

# Optional: Use gRPC for better performance
export RAGDEX_VECTOR_STORE_PREFER_GRPC=true
export RAGDEX_VECTOR_STORE_GRPC_PORT=6334
```

**Example - Docker QDrant:**
```bash
# Start QDrant with Docker
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Configure ragdex to use it
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=remote
export RAGDEX_VECTOR_STORE_URL=http://localhost:6333
ragdex-mcp
```

**Example - QDrant Cloud:**
```bash
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=remote
export RAGDEX_VECTOR_STORE_URL=https://your-cluster.cloud.qdrant.io
export RAGDEX_VECTOR_STORE_API_KEY=your_api_key
ragdex-mcp
```

## Advanced Configuration

### Distance Metrics

QDrant supports different distance metrics (ChromaDB uses cosine by default):

```bash
export RAGDEX_VECTOR_STORE_DISTANCE=COSINE  # COSINE, EUCLID, or DOT
```

### Collection Names

Use different collections for different document sets:

```bash
export RAGDEX_VECTOR_STORE_COLLECTION_NAME=work_docs
```

### Vector Size

The vector size is auto-detected from your embedding model, but you can override it:

```bash
export RAGDEX_VECTOR_STORE_VECTOR_SIZE=768
```

## Migration Between Vector Databases

To migrate from ChromaDB to QDrant (or vice versa):

1. **Export your documents** (if needed for backup)
2. **Change configuration** to the new vector store
3. **Re-index your documents**:
   ```bash
   ragdex-index
   ```

The indexing process will detect existing documents and rebuild the vector store.

## Performance Comparison

| Feature | ChromaDB | QDrant (Local) | QDrant (Remote) |
|---------|----------|----------------|-----------------|
| Setup Complexity | ⭐ Easy | ⭐ Easy | ⭐⭐ Moderate |
| Search Speed | ⭐⭐ Good | ⭐⭐⭐ Fast | ⭐⭐⭐ Fast |
| Scalability | ⭐⭐ Limited | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Excellent |
| Persistence | ⭐⭐⭐ Auto | ⭐⭐⭐ Auto | ⭐⭐⭐ Auto |
| Multi-process | ❌ No | ✅ Yes | ✅ Yes |
| Filtering | ⭐⭐ Basic | ⭐⭐⭐ Advanced | ⭐⭐⭐ Advanced |

## Troubleshooting

### QDrant Connection Issues

If you get connection errors with remote QDrant:

```bash
# Verify QDrant is running
curl http://localhost:6333/health

# Check QDrant status
curl http://localhost:6333/collections
```

### Import Errors

If you get `ImportError: QDrant is not installed`:

```bash
pip install qdrant-client
```

### Performance Issues

For better performance with remote QDrant, enable gRPC:

```bash
export RAGDEX_VECTOR_STORE_PREFER_GRPC=true
```

### Collection Already Exists

If you change vector size or distance metric, you may need to delete the existing collection:

**ChromaDB:**
```bash
rm -rf ~/.local/share/personal_doc_library/chroma_db
ragdex-index  # Re-index
```

**QDrant (local):**
```bash
rm -rf ~/.local/share/personal_doc_library/chroma_db
ragdex-index  # Re-index
```

**QDrant (remote):**
```bash
# Use QDrant API or dashboard to delete collection
curl -X DELETE http://localhost:6333/collections/ragdex
ragdex-index  # Re-index
```

## Complete Configuration Examples

### Example 1: Simple Local Setup (ChromaDB)
```bash
# .env file or shell
export PERSONAL_LIBRARY_DOC_PATH=~/Documents/Books
export PERSONAL_LIBRARY_DB_PATH=~/ragdex_data

# No need to set RAGDEX_VECTOR_STORE_TYPE - ChromaDB is default
ragdex-mcp
```

### Example 2: Local QDrant for Better Performance
```bash
# .env file
export PERSONAL_LIBRARY_DOC_PATH=~/Documents/Books
export PERSONAL_LIBRARY_DB_PATH=~/ragdex_data
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=local
export RAGDEX_VECTOR_STORE_COLLECTION_NAME=my_library

ragdex-mcp
```

### Example 3: Production Setup with Remote QDrant
```bash
# .env file
export PERSONAL_LIBRARY_DOC_PATH=/data/documents
export PERSONAL_LIBRARY_DB_PATH=/data/ragdex
export RAGDEX_VECTOR_STORE_TYPE=qdrant
export RAGDEX_VECTOR_STORE_MODE=remote
export RAGDEX_VECTOR_STORE_URL=http://qdrant-server:6333
export RAGDEX_VECTOR_STORE_API_KEY=production_key
export RAGDEX_VECTOR_STORE_COLLECTION_NAME=prod_docs
export RAGDEX_VECTOR_STORE_PREFER_GRPC=true

ragdex-mcp
```

## Future Vector Database Support

The vector database abstraction layer is designed to be extensible. Future versions may support:

- **Pinecone**: Cloud-native vector database
- **Weaviate**: GraphQL-based vector search engine
- **Milvus**: Open-source vector database for AI applications
- **FAISS**: Facebook AI Similarity Search library

Want to add support for another vector database? Check out the [contribution guide](CONTRIBUTING.md) or open an issue on GitHub!

## Architecture

The vector database abstraction layer follows the adapter pattern:

```
┌─────────────────┐
│   SharedRAG     │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  VectorStoreFactory │
└────────┬────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│ ChromaDB│ │ QDrant  │
│ Adapter │ │ Adapter │
└─────────┘ └─────────┘
```

Each adapter implements a common interface, making it easy to switch between vector databases without changing application code.

## Questions or Issues?

- **Documentation**: Check the [README](README.md) for general usage
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/hpoliset/ragdex/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/hpoliset/ragdex/discussions)
