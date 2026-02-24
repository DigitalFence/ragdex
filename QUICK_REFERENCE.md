# Quick Reference - Ragdex (RAG Document Indexer for MCP)

## Package Installation

### Install from PyPI
```bash
# Using uv (recommended)
uv venv ~/ragdex_env
cd ~/ragdex_env
uv pip install ragdex

# Or using pip
pip install ragdex

# With optional extras
pip install 'ragdex[doc-support,services]'
```

### Install from Source (Development)
```bash
# Clone and install in editable mode
git clone https://github.com/hpoliset/ragdex
cd ragdex
pip install -e .

# With optional extras
pip install -e ".[doc-support,services]"
```

## Optional System Dependencies

These are **not required** for basic operation but enable additional format support:

| Tool | Command | Purpose | Install (macOS) |
|------|---------|---------|-----------------|
| **Calibre** | `ebook-convert` | MOBI/AZW/AZW3 ebooks | `brew install --cask calibre` |
| **LibreOffice** | `soffice` | Legacy `.doc` files | `brew install --cask libreoffice` |
| **ocrmypdf** | `ocrmypdf` | OCR for scanned PDFs | `brew install ocrmypdf tesseract` |
| **Ghostscript** | `gs` | Clean corrupted PDFs | `brew install ghostscript` |

> **Note**: Poppler is **not required** — Ragdex uses pure-Python PDF libraries. Linux support is untested.

```bash
# Install all optional tools at once (macOS)
brew install --cask calibre libreoffice
brew install ocrmypdf tesseract ghostscript
```

## Installation with Specific Python Version

### Using uv (Recommended)

```bash
# Option 1: Specify version number (uv will find it)
uv venv --python 3.13 ragdex_env
source ragdex_env/bin/activate

# Option 2: Specify exact Python executable
uv venv --python python3.13 ragdex_env
source ragdex_env/bin/activate

# Option 3: Use full path to Python
uv venv --python /opt/homebrew/opt/python@3.13/bin/python3.13 ragdex_env
source ragdex_env/bin/activate

# Install ragdex
uv pip install ragdex
```

**Supported Python versions:** 3.9, 3.10, 3.11, 3.12, 3.13

## Command-Line Tools (After Installation)

### 1. `ragdex` - Main CLI Tool
**Purpose:** Configuration and management utility

```bash
ragdex --help                       # Show all available subcommands
ragdex config                       # Configure library paths and settings
ragdex ensure-dirs                  # Create required directory structure
ragdex index-status                 # Check indexing status
ragdex find-unindexed               # Find documents not yet indexed
ragdex fix-skipped                  # Retry failed document processing
ragdex manage-failed                # View and manage failed documents
```

**When to use:** Initial setup, checking status, troubleshooting

---

### 2. `ragdex-mcp` - MCP Server
**Purpose:** Model Context Protocol server for Claude Desktop integration

This is the **main service** that Claude connects to. It provides 17 MCP tools for searching and analyzing your document library.

```bash
# Run manually for testing
ragdex-mcp

# In Claude Desktop config
"command": "/path/to/your/venv/bin/ragdex-mcp"
```

**Features:**
- Background thread initialization (v0.3.1+)
- Configurable warmup with `MCP_WARMUP_ON_START`
- 17 MCP tools (search, find_practices, compare_perspectives, etc.)
- Handles RAG queries from Claude

**When to use:**
- Configured in Claude Desktop (runs automatically)
- Manual testing of MCP server startup

---

### 3. `ragdex-index` - Background Indexer
**Purpose:** Monitors document directory and automatically indexes new/modified files

This **indexing service** watches for changes and processes documents in the background.

```bash
# Run manually
ragdex-index

# Clear failed documents list and re-attempt on next sync
ragdex-index --retry

# Installed as service via
./setup_services.sh              # PyPI installation
./install.sh --with-services     # Source installation
```

**What it does:**
- Watches document directory for changes
- Automatically processes PDFs, Word docs, EPUBs, MOBI, emails
- Extracts text and generates embeddings
- Updates ChromaDB vector database
- Tracks failed documents

**Flags:**
- `--retry` — Clears the failed documents list (`failed_pdfs.json`) so all previously failed files are re-attempted on the next sync cycle
- `--daemon` — Run as background daemon process
- `--service` — Service mode (longer delays, lower priority)
- `--books-dir PATH` — Override document directory
- `--db-dir PATH` — Override database directory

**When to use:**
- Install as background service for automatic indexing
- Run manually for one-time indexing
- Use `--retry` after installing missing tools (e.g., LibreOffice, Ghostscript) to re-process previously failed documents

---

### 4. `ragdex-web` - Web Dashboard
**Purpose:** Web-based monitoring interface

View real-time indexing progress and library statistics at http://localhost:8888 (PyPI) or http://localhost:9999 (source).

```bash
# Run manually
ragdex-web

# Installed as service via
./setup_services.sh              # Port 8888
./install.sh --with-services     # Port 9999
```

**Features:**
- Real-time indexing progress
- Library statistics (books, chunks, categories)
- Recently indexed documents
- Failed document tracking
- Search functionality with Enter key support

**When to use:**
- Monitor indexing progress
- Browse library statistics
- Debug failed documents
- Search your library via web interface

## Traditional Scripts (Alternative)

### Starting the Server
```bash
# Run MCP server (from project root)
./scripts/run.sh

# Index only
./scripts/run.sh --index-only

# Index with retry
./scripts/run.sh --index-only --retry
```

### Background Monitoring
```bash
# Start background monitor
./scripts/index_monitor.sh

# Stop monitor
./scripts/stop_monitor.sh

# Check service status
./scripts/service_status.sh
```

### Web Interface
```bash
# Using package command
ragdex-web

# Or traditional method (if using source)
./scripts/start_web_monitor.sh

# Access at http://localhost:8888
```

### Service Installation
```bash
# Install as LaunchAgent
./scripts/install_service.sh
./scripts/install_webmonitor_service.sh

# Uninstall services
./scripts/uninstall_service.sh
./scripts/uninstall_webmonitor_service.sh

# Check status
./scripts/service_status.sh
./scripts/webmonitor_service_status.sh
```

## MCP Protocol Features

### Tools (17 Available)
```
Search & Discovery:
- search                  # Semantic search with synthesis
- list_books             # List by pattern/author
- recent_books           # Find recent additions
- find_practices         # Find specific techniques

Content Extraction:
- extract_pages          # Extract specific pages
- extract_quotes         # Find notable quotes
- summarize_book         # Generate AI summaries

Analysis & Synthesis:
- compare_perspectives   # Compare across sources
- question_answer        # Direct Q&A
- daily_reading          # Suggested passages

System Management:
- library_stats          # Library statistics
- index_status           # Indexing progress
- refresh_cache          # Refresh search cache
- warmup                 # Initialize RAG system
- find_unindexed         # Find unindexed docs
- reindex_book           # Force reindex
- clear_failed           # Clear failed list
```

### Prompts (5 Templates)
```
- analyze_theme          # Theme analysis
- compare_authors        # Author comparison
- extract_practices      # Extract techniques
- research_topic         # Deep research
- daily_wisdom           # Daily wisdom
```

### Resources (4 Dynamic)
```
- library://stats        # Current statistics
- library://recent       # Recent additions
- library://search-tips  # Usage examples
- library://config       # Configuration
```

## Testing

### Test MCP Features
```bash
# Test protocol implementation
python test_mcp_features.py

# Test resources functionality
python test_resources.py

# Test search functionality
python tests/test_search_simple.py
```

### Manual Testing
```bash
# Using venv directly
venv_mcp/bin/python -m personal_doc_library.servers.mcp_complete_server

# Test specific modules
venv_mcp/bin/python -c "
from personal_doc_library.core.shared_rag import SharedRAG
rag = SharedRAG()
print(f'Books: {rag.get_book_count()}')
"
```

## File Locations

### Source Code (New Package Structure)
- **Package**: `src/personal_doc_library/`
- **MCP Server**: `src/personal_doc_library/servers/mcp_complete_server.py`
- **RAG System**: `src/personal_doc_library/core/shared_rag.py`
- **Configuration**: `src/personal_doc_library/core/config.py`
- **CLI**: `src/personal_doc_library/cli.py`

### Data Directories
- **Books**: `books/` or `$PERSONAL_LIBRARY_DOC_PATH`
- **Database**: `chroma_db/` or `$PERSONAL_LIBRARY_DB_PATH`
- **Logs**: `logs/` or `$PERSONAL_LIBRARY_LOGS_PATH`

### Configuration Files
- **Package Config**: `pyproject.toml`
- **Dependencies**: `requirements.txt`
- **Claude Config**: `~/Library/Application Support/Claude/claude_desktop_config.json`

## Claude Desktop Configuration

Update your `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ragdex": {
      "command": "/Users/YOUR_USERNAME/ragdex_env/bin/ragdex-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CHROMA_TELEMETRY": "false",
        "PERSONAL_LIBRARY_DOC_PATH": "/path/to/books",
        "PERSONAL_LIBRARY_DB_PATH": "/path/to/database",
        "PERSONAL_LIBRARY_LOGS_PATH": "/path/to/logs",
        "MCP_WARMUP_ON_START": "true",
        "MCP_INIT_TIMEOUT": "30",
        "MCP_TOOL_TIMEOUT": "15"
      }
    }
  }
}
```

## Environment Variables

```bash
# Set document paths
export PERSONAL_LIBRARY_DOC_PATH="/path/to/books"
export PERSONAL_LIBRARY_DB_PATH="/path/to/database"
export PERSONAL_LIBRARY_LOGS_PATH="/path/to/logs"

# MCP Performance (v0.3.0+)
export MCP_WARMUP_ON_START=true       # Pre-initialize on server start
export MCP_INIT_TIMEOUT=30            # Seconds for initialization
export MCP_TOOL_TIMEOUT=15            # Seconds for tool timeout

# Disable telemetry
export CHROMA_TELEMETRY=false
export TOKENIZERS_PARALLELISM=false
export ANONYMIZED_TELEMETRY=false
```

## Troubleshooting

### Import Errors
```bash
# Ensure package is installed
pip install -e .

# Or set PYTHONPATH manually
export PYTHONPATH="/path/to/ragdex/src:${PYTHONPATH:-}"
```

### Service Issues
```bash
# Check logs
tail -f logs/index_monitor_stderr.log
tail -f logs/webmonitor_stdout.log

# View MCP logs
./scripts/view_mcp_logs.sh

# Reset services
./scripts/uninstall_service.sh
./scripts/install_service.sh
```

### Indexing Problems
```bash
# Check status
ragdex check-indexing-status

# Find unindexed
ragdex find-unindexed

# Manage failed documents
ragdex manage-failed-pdfs

# Force reindex (if using source)
./scripts/run.sh --index-only --retry
```

### Memory Issues
```bash
# Set memory limit for indexing
export INDEXING_MEMORY_LIMIT_GB=8
./scripts/run.sh --index-only --retry
```

## Common Workflows

### Initial Setup
```bash
pip install ragdex
ragdex ensure-dirs
ragdex config
ragdex-mcp  # Start server
```

### Daily Use
```bash
# Option 1: Package commands
ragdex-web &        # Start web dashboard
ragdex-index &      # Start indexer
ragdex-mcp          # Run MCP server

# Option 2: Services (macOS)
# Download and run service setup
curl -O https://raw.githubusercontent.com/hpoliset/ragdex/main/setup_services.sh
chmod +x setup_services.sh
./setup_services.sh
# Services run automatically

# Option 3: Manual scripts (if using source)
./scripts/index_monitor.sh &
./scripts/start_web_monitor.sh &
./scripts/run.sh
```

### Development
```bash
# Edit code
vim src/personal_doc_library/servers/mcp_complete_server.py

# Test changes
python test_mcp_features.py

# Restart Claude Desktop to apply changes
```