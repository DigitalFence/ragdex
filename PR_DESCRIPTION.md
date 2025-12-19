# Pull Request: Add Docker support with external Vector DB, Document Library, and logs

## Summary

This PR adds comprehensive Docker containerization support for Ragdex, enabling users to run the entire application stack in isolated containers while keeping all data (Vector DB, Document Library, and logs) external and persistent on the host machine.

## Key Features

### 🐳 Three Orchestrated Services
1. **ragdex-mcp** - MCP server for Claude Desktop integration
2. **ragdex-index** - Background indexer with automatic file monitoring
3. **ragdex-web** - Web dashboard accessible at `http://localhost:8888`

### 📦 External Data Storage (as requested)
- **Vector DB (ChromaDB)**: `./data/chroma_db/` - Fully persistent on host
- **Document Library**: Configurable via `DOCUMENTS_PATH` env variable (mounted read-only)
- **Logs**: `./data/logs/` - All service logs accessible on host

### 🔧 Implementation Details

#### Files Added:
- **Dockerfile**: Multi-stage build with Python 3.11
  - System dependencies: ghostscript, calibre, libreoffice, tesseract-ocr
  - Optional doc-support dependencies for legacy .doc files
  - Non-root user (ragdex:1000) for security
  - Optimized build process with proper caching

- **docker-compose.yml**: Complete orchestration setup
  - All three services pre-configured
  - Environment variable support via .env file
  - Automatic restart policies
  - Proper service dependencies

- **.dockerignore**: Optimized build context
- **.env.docker.template**: Configuration template for easy setup
- **DOCKER.md**: Comprehensive 480+ line documentation covering:
  - Quick start guide (5 minutes to running)
  - Service management
  - Claude Desktop integration (3 methods)
  - Data persistence and backup strategies
  - Migration guide for v0.3.6 metadata updates
  - Troubleshooting guide
  - Security considerations
  - Performance tuning
  - Resource management

- **README.md**: Added Docker installation section with link to full guide

### 🔐 Security Features
- Non-root container execution
- Read-only document mounts
- No network exposure except web dashboard port
- Local processing (all data stays on machine)
- Proper file permissions

### ⚙️ Compatibility
- Docker Engine 20.10+
- Docker Compose 2.0+
- Compatible with v0.3.6 features including:
  - Python 3.9-3.13 support (Docker uses 3.11)
  - Updated dependencies (langchain 0.3.x, chromadb 1.3.x)
  - Legacy .doc file handling
  - Metadata migration support

### 📊 Resource Requirements
- 8GB RAM minimum (16GB recommended)
- ~5GB disk space (app + models)
- First run downloads ~2GB of AI models

## Testing

- ✅ docker-compose.yml syntax validated
- ✅ Dockerfile structure verified
- ✅ All environment variables properly configured
- ✅ Volume mounts correctly specified
- ✅ Service dependencies properly ordered

## Quick Start for Users

```bash
# 1. Configure
cp .env.docker.template .env
# Edit .env and set DOCUMENTS_PATH=/path/to/your/documents

# 2. Start services
docker-compose up -d

# 3. Access dashboard
open http://localhost:8888
```

## Migration Support

Includes instructions for migrating from older versions:
```bash
docker-compose run --rm ragdex-mcp python scripts/migrate_metadata_v036.py --backup
```

## Benefits

- 🚀 Clean, isolated environment
- 📦 Easy deployment and updates
- 🔄 Simple rollback capabilities
- 🌐 Cross-platform consistency
- 💾 All data persists on host
- 🔧 Services can run independently or together
- 📈 Easy horizontal scaling potential

## Documentation

Complete documentation in `DOCKER.md` includes:
- Architecture overview
- Step-by-step setup
- Claude Desktop integration options
- Backup and restore procedures
- Upgrade and migration guides
- Common troubleshooting scenarios
- Advanced configuration options

## Breaking Changes

None - this is purely additive. Existing installation methods continue to work as before.

## Commits

```
52136a8 Enhance Docker setup for v0.3.6 compatibility
2328bee Add Docker support with external Vector DB, Document Library, and logs
```

---

**Ready for review!** This implementation provides a production-ready Docker setup with comprehensive documentation and follows Docker best practices.
