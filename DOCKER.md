# Running Ragdex in Docker

This guide explains how to run Ragdex in Docker containers with external Vector DB, Document Library, and logs.

## Architecture

The Docker setup includes three services:

1. **ragdex-mcp** - MCP server for Claude Desktop integration
2. **ragdex-index** - Background indexer that monitors and indexes documents
3. **ragdex-web** - Web dashboard at `http://localhost:9999` (host port 9999 → container 8888)

All services share access to:
- **External Vector DB** (ChromaDB) - stored in `./data/chroma_db`
- **External Document Library** - your documents (read-only mount)
- **External Logs** - stored in `./data/logs`

**Docker Image:** Uses Python 3.11 with full document processing support (PDF, Office, E-books) and optional legacy .doc file handling.

## Docker or native — pick one per index

Docker is an **alternative** to the native install (see the README Quick Start),
not a supplement. Both read/write the same kind of ChromaDB store, so:

- Point Docker at a **fresh** `DB_PATH` for an independent index, **or** at an
  existing `chroma_db` to reuse a native index (works when the image and your
  native install share the same `chromadb`/`langchain`/`sentence-transformers`
  versions).
- **Do not run the native indexer and the Docker indexer against the same
  `chroma_db` at the same time** — two writers on one store will contend. Run
  only one indexer per database (stop/disable the other, or give each its own
  `DB_PATH`).

## Platform support

The image is built `FROM python:3.11-slim` (Debian) and is architecture-agnostic:

- **macOS (Apple Silicon)** via Docker Desktop — the reference setup. Note the
  CPU-only PyTorch and `cryptography<43` pins in the Dockerfile, which avoid
  SIGILL crashes under Docker Desktop's ARM virtualization.
- **Linux (x86_64 and arm64)** — `docker compose build` produces a native image
  for the host architecture. The same pins apply and are harmless there (CPU
  PyTorch is the default for this CPU embedding workload; GPU users can adjust).

On macOS, mounted host paths must be shared with Docker Desktop (Settings →
Resources → File Sharing); iCloud/CloudDocs paths are not visible to containers.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 8GB RAM available for Docker
- ~5GB disk space for images and models

## Quick Start

### 1. Clone and Navigate

```bash
git clone https://github.com/DigitalFence/ragdex.git
cd ragdex
```

### 2. Configure Environment

Create a `.env` file from the template:

```bash
cp .env.docker.template .env
```

Edit `.env` and set your documents path:

```bash
# For Linux/macOS
DOCUMENTS_PATH=/home/yourusername/Documents

# For Windows (use forward slashes)
DOCUMENTS_PATH=C:/Users/yourusername/Documents
```

### 3. Create Data Directories

```bash
mkdir -p data/chroma_db data/documents data/logs
```

### 4. Build and Start Services

```bash
# Build the Docker image
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Access the Web Dashboard

Open your browser to: `http://localhost:9999`

## Configuration

### Using Your Document Library

There are two ways to mount your documents:

#### Option 1: Using .env file (Recommended)

Edit `.env`:
```bash
DOCUMENTS_PATH=/path/to/your/documents
```

Then start services:
```bash
docker-compose up -d
```

#### Option 2: Direct Override

```bash
DOCUMENTS_PATH=/path/to/your/documents docker-compose up -d
```

### Email Indexing (Optional)

To enable email indexing, edit `.env`:

```bash
INDEX_EMAILS=true
EMAIL_MAX_AGE_DAYS=365
```

Note: Email paths must also be mounted if emails are stored outside your documents path.

## Managing Services

### Start All Services

```bash
docker-compose up -d
```

### Start Specific Service

```bash
# Only web dashboard
docker-compose up -d ragdex-web

# Only background indexer
docker-compose up -d ragdex-index

# MCP server (stdio) — for standalone testing only; Claude Desktop launches
# its own container via `docker run` (see "Integration with Claude Desktop")
docker-compose --profile mcp run --rm ragdex-mcp
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop specific service
docker-compose stop ragdex-web
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart ragdex-index
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ragdex-web

# Last 100 lines
docker-compose logs --tail=100 ragdex-index
```

## Data Persistence

All data is stored externally on your host machine:

### Vector Database (ChromaDB)
- **Location:** `DB_PATH` (default `./data/chroma_db/`)
- **Contents:**
  - `chroma.sqlite3` - Vector database
  - `book_index.json` - Document metadata
  - `index_status.json` - Indexing progress
  - `failed_pdfs.json` - Failed document tracking

### Document Library
- **Location:** Your configured `DOCUMENTS_PATH`
- **Access:** Read-only (documents are never modified)
- **Supported formats:** PDF, DOCX, PPTX, EPUB, MOBI, TXT, etc.

### Logs
- **Location:** `LOGS_PATH` (default `./data/logs/`)
- **Contents:**
  - `mcp_server_YYYYMMDD.log`
  - `indexing_YYYYMMDD.log`
  - `monitor_YYYYMMDD.log`
  - `ragdex_*.log`

### Backing Up Your Data

```bash
# Backup Vector DB
tar -czf ragdex_db_backup_$(date +%Y%m%d).tar.gz data/chroma_db/

# Backup Logs
tar -czf ragdex_logs_backup_$(date +%Y%m%d).tar.gz data/logs/
```

## Integration with Claude Desktop

The MCP protocol runs over **stdio**: Claude Desktop launches the server as a
subprocess and talks to it through stdin/stdout. The robust way to do this with
Docker is to have Claude Desktop launch a fresh container per session with
`docker run -i --rm` — no long-running MCP container is required (and the
`ragdex-mcp` compose service is intentionally *not* started by `docker compose
up`; see docker-compose.yml).

### Prerequisites

1. **Build the image** once so the `ragdex:latest` tag exists:
   ```bash
   docker compose build
   ```
2. **Docker Desktop must be running** whenever you use the library in Claude
   Desktop — the MCP server runs inside a container it launches on demand.

### Configuration (recommended: `docker run`)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`. Point the
volume mounts at your real data — you can **reuse an existing local index** by
mounting your current `chroma_db` (no re-indexing needed if the image and your
prior install share the same `chromadb`/`langchain`/`sentence-transformers`
versions):

```json
{
  "mcpServers": {
    "spiritual-library": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/absolute/path/to/documents:/data/documents:ro",
        "-v", "/absolute/path/to/chroma_db:/data/chroma_db",
        "-v", "/absolute/path/to/logs:/data/logs",
        "-e", "PERSONAL_LIBRARY_DOC_PATH=/data/documents",
        "-e", "PERSONAL_LIBRARY_DB_PATH=/data/chroma_db",
        "-e", "PERSONAL_LIBRARY_LOGS_PATH=/data/logs",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "TOKENIZERS_PARALLELISM=false",
        "-e", "MCP_WARMUP_ON_START=true",
        "ragdex:latest",
        "ragdex-mcp"
      ]
    }
  }
}
```

Notes:
- `-i` keeps stdin open (required for stdio); `--rm` cleans up the container when
  Claude Desktop closes the connection.
- `MCP_WARMUP_ON_START=true` pre-loads the embedding model and vector store in
  the background at launch so the first tool call doesn't return a "still
  initializing" message. Omit it to save memory at the cost of a slower first
  query.
- The document mount is read-only (`:ro`); the DB and logs mounts are read-write.
- On macOS, Docker Desktop must have **file-sharing access** to the mounted host
  paths (Settings → Resources → File Sharing). iCloud/CloudDocs paths are not
  visible to containers — use a local folder.
- Restart Claude Desktop after editing the config.

### Background indexer + web dashboard

Run these as always-on services with the **same** data paths (via `.env`), so the
indexer keeps the shared vector store up to date while Claude Desktop queries it:

```bash
# .env sets DOCUMENTS_PATH, DB_PATH, LOGS_PATH to the same host paths used above
docker compose up -d        # starts ragdex-index + ragdex-web
```

### Standalone MCP for testing

To exercise the MCP server manually without Claude Desktop:

```bash
docker compose --profile mcp run --rm ragdex-mcp
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
docker info

# Check Docker Compose version
docker-compose version

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### No Documents Being Indexed

```bash
# Check if documents path is mounted correctly
docker-compose exec ragdex-index ls -la /data/documents

# Check indexer logs
docker-compose logs ragdex-index

# Verify permissions
ls -la $DOCUMENTS_PATH
```

### Web Dashboard Not Accessible

```bash
# Check if service is running
docker-compose ps ragdex-web

# Check port binding
docker-compose port ragdex-web 8888

# Check logs
docker-compose logs ragdex-web

# Try accessing (host port; default 9999)
curl http://localhost:9999
```

### High Memory Usage

```bash
# Check memory usage
docker stats

# Limit memory in docker-compose.yml
services:
  ragdex-web:
    mem_limit: 4g
    mem_reservation: 2g
```

### ChromaDB Issues

```bash
# Check database directory
ls -la data/chroma_db/

# Reset database (WARNING: deletes all indexed data)
rm -rf data/chroma_db/*
docker-compose restart
```

### Model Downloads Failing

The embedding model (~2GB) downloads on first run. If it fails:

```bash
# Check disk space
df -h

# Check logs for download errors
docker-compose logs ragdex-mcp | grep -i download

# Manually pre-download (from host)
docker-compose run --rm ragdex-mcp python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"
```

## Advanced Configuration

### Custom Dockerfile Modifications

If you need additional system packages:

```dockerfile
# Add to Dockerfile after the RUN apt-get install section
RUN apt-get update && apt-get install -y \
    your-package-here \
    && apt-get clean
```

Rebuild:
```bash
docker-compose build --no-cache
```

### Using Named Volumes Instead of Bind Mounts

Edit `docker-compose.yml`:

```yaml
services:
  ragdex-web:
    volumes:
      - chroma_db:/data/chroma_db  # Named volume
      - ${DOCUMENTS_PATH}:/data/documents:ro
      - logs:/data/logs  # Named volume

volumes:
  chroma_db:
    driver: local
  logs:
    driver: local
```

### Resource Limits

Add to each service in `docker-compose.yml`:

```yaml
services:
  ragdex-web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G
```

### Running on Different Port

The web dashboard is published on host port **9999** by default (container
listens on 8888). To change the host port, set `WEB_PORT` in your `.env`:

```bash
WEB_PORT=7777
```

Or edit the mapping directly in `docker-compose.yml`:

```yaml
services:
  ragdex-web:
    ports:
      - "7777:8888"  # Access on port 7777
```

## Security Considerations

1. **Read-Only Document Mount:** Documents are mounted read-only by default
2. **Non-Root User:** Container runs as user `ragdex` (UID 1000)
3. **No Network Exposure:** Only web dashboard port is exposed
4. **Local Processing:** All data stays on your machine

## Performance Tuning

### Faster Indexing

Set environment variable in `docker-compose.yml`:

```yaml
environment:
  - WORKERS=4  # Parallel processing
```

### Reduce Model Size

Use a smaller embedding model:

```yaml
environment:
  - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Updating Ragdex

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --pull
docker-compose up -d

# Verify versions
docker-compose exec ragdex-mcp pip show personal-doc-library
```

### Migrating Metadata (v0.3.6+)

If upgrading to v0.3.6+ from an earlier version, you may need to migrate metadata:

```bash
# Stop services to ensure clean migration
docker-compose down

# Run migration script inside container
docker-compose run --rm ragdex-mcp python scripts/migrate_metadata_v036.py --backup

# Restart services
docker-compose up -d
```

The migration adds folder and relative path metadata to existing documents without requiring full re-indexing.

## Uninstalling

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove data (WARNING: deletes indexed data)
rm -rf data/

# Remove downloaded models
docker volume prune
```

## Getting Help

- **Issues:** https://github.com/DigitalFence/ragdex/issues
- **Documentation:** https://github.com/DigitalFence/ragdex#readme
- **Logs:** Check `data/logs/` for detailed error messages

## License

MIT License - See LICENSE file for details
