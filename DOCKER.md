# Running Ragdex in Docker

This guide explains how to run Ragdex in Docker containers with external Vector DB, Document Library, and logs.

## Architecture

The Docker setup includes three services:

1. **ragdex-mcp** - MCP server for Claude Desktop integration
2. **ragdex-index** - Background indexer that monitors and indexes documents
3. **ragdex-web** - Web dashboard at `http://localhost:8888`

All services share access to:
- **External Vector DB** (ChromaDB) - stored in `./data/chroma_db`
- **External Document Library** - your documents (read-only mount)
- **External Logs** - stored in `./data/logs`

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 8GB RAM available for Docker
- ~5GB disk space for images and models

## Quick Start

### 1. Clone and Navigate

```bash
git clone https://github.com/yourusername/ragdex.git
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

Open your browser to: `http://localhost:8888`

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

# Only MCP server
docker-compose up -d ragdex-mcp
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
- **Location:** `./data/chroma_db/`
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
- **Location:** `./data/logs/`
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

To use the Dockerized MCP server with Claude Desktop:

### Option 1: Docker Socket Mount (Advanced)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ragdex": {
      "command": "docker",
      "args": ["exec", "-i", "ragdex-mcp", "ragdex-mcp"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Option 2: Stdio Bridge (Recommended)

Create a wrapper script `ragdex-docker-bridge.sh`:

```bash
#!/bin/bash
docker exec -i ragdex-mcp ragdex-mcp
```

Make it executable:
```bash
chmod +x ragdex-docker-bridge.sh
```

Then configure Claude Desktop:
```json
{
  "mcpServers": {
    "ragdex": {
      "command": "/path/to/ragdex-docker-bridge.sh",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Option 3: Network Bridge (Future)

For network-based MCP protocol (when supported), you can expose the MCP server on a port.

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

# Try accessing
curl http://localhost:8888
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

Edit `docker-compose.yml`:

```yaml
services:
  ragdex-web:
    ports:
      - "9999:8888"  # Access on port 9999
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

- **Issues:** https://github.com/anthropics/ragdex/issues
- **Documentation:** https://docs.claude.com/
- **Logs:** Check `data/logs/` for detailed error messages

## License

MIT License - See LICENSE file for details
