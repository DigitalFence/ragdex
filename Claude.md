# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Ragdex** is a production-ready MCP (Model Context Protocol) server that enables Claude to access and analyze a personal collection of documents and emails through RAG (Retrieval-Augmented Generation). The system supports multiple document formats (PDFs, Word documents, EPUBs, MOBI/AZW/AZW3 ebooks) and email archives (Apple Mail EMLX, Outlook OLM), featuring automatic indexing, real-time monitoring, smart filtering, and robust error handling.

**Current Status**: ✅ **FULLY OPERATIONAL** v0.2.0 with ARM64 compatibility, 768-dim embeddings, 17 MCP tools, email support, and smart filtering.

## Repository Structure

```
ragdex/
├── src/personal_doc_library/  # Main source code
│   ├── core/              # Core functionality (shared_rag.py, config.py, logging)
│   ├── servers/           # MCP server implementation
│   ├── indexing/          # Document indexing tools
│   ├── loaders/           # Email loaders (EMLX, Outlook)
│   ├── monitoring/        # Web monitoring interface
│   └── utils/             # Utility scripts
├── scripts/               # Shell scripts for running the system
├── tests/                 # Test files
├── config/                # Configuration templates
├── logs/                 # Log files (gitignored)
├── books/                # Document library (gitignored)
├── chroma_db/            # Vector database (gitignored)
└── docs/                 # Documentation files
```

## Architecture Overview

The system follows a **modular, service-oriented architecture**:

1. **MCP Complete Server** (`src/personal_doc_library/servers/mcp_complete_server.py`): Main MCP server with 17 tools
2. **Shared RAG System** (`src/personal_doc_library/core/shared_rag.py`): Core RAG functionality with vector storage
3. **Index Monitor** (`src/personal_doc_library/indexing/index_monitor.py`): Background service for automatic indexing
4. **Web Monitor** (`src/personal_doc_library/monitoring/monitor_web_enhanced.py`): Real-time dashboard (localhost:8888) with Enter key search support
5. **Configuration System** (`src/personal_doc_library/core/config.py`): Centralized path and settings management

### MCP Tools Available (17 total)
- **search**: Search library with optional book/email filtering and synthesis
- **find_practices**: Find specific practices or techniques
- **compare_perspectives**: Compare perspectives across sources
- **library_stats**: Get library statistics and indexing status
- **index_status**: Get detailed indexing status
- **summarize_book**: Generate AI summary of a book
- **extract_quotes**: Find notable quotes on topics
- **daily_reading**: Get suggested daily passages
- **question_answer**: Direct Q&A from library
- **refresh_cache**: Refresh search cache and reload index
- **warmup**: Initialize RAG system to prevent timeouts
- **list_books**: List books by pattern/author/directory
- **recent_books**: Find recently indexed books
- **extract_pages**: Extract specific pages from books
- **find_book_by_metadata**: Search by title/author/publisher
- **get_book_metadata**: Get detailed book metadata
- **search_by_date_range**: Search within date ranges

### Key Architectural Patterns
- **Lazy Loading**: RAG system initialized only when needed to avoid MCP timeouts
- **File-based Locking**: Cross-process coordination with 30-minute stale lock detection
- **Event-Driven Processing**: File system events trigger automatic indexing
- **Batch Processing**: Documents chunked and processed efficiently
- **Circuit Breaker**: 15-minute timeout protection for long operations

## Essential Commands

```bash
# Initial setup
./install.sh                     # Interactive setup (source installation)
./setup_services.sh              # Setup services after PyPI installation
pip install -r requirements.txt  # Install dependencies (if manual setup)

# Running the system
./scripts/run.sh                # Run MCP server (default mode)
./scripts/run.sh --index-only   # Index documents only
./scripts/run.sh --index-only --retry  # Index with retry and memory monitoring

# Service management
./scripts/install_service.sh    # Install as LaunchAgent service
./scripts/service_status.sh     # Check service health
./scripts/uninstall_service.sh  # Remove service

# Background monitoring
./scripts/index_monitor.sh      # Start background monitor
./scripts/stop_monitor.sh       # Stop background monitor

# Web monitoring
export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"
python -m personal_doc_library.monitoring.monitor_web_enhanced  # Start web dashboard (http://localhost:8888)

# Debugging
./scripts/test_logs.sh          # Test log viewing
./scripts/view_mcp_logs.sh      # View MCP server logs
./scripts/indexing_status.sh    # Check indexing status
```

## Publishing to PyPI

### Via GitHub Actions (recommended)
1. Bump the version in `pyproject.toml`
2. Commit and push to `main`
3. Trigger the publish workflow:
```bash
# Publish to PyPI
gh workflow run publish.yml --ref main -f test_pypi=false

# Publish to TestPyPI first (for validation)
gh workflow run publish.yml --ref main -f test_pypi=true
```

The workflow also auto-publishes when a GitHub Release is created.

### Via Local (fallback)
```bash
uv build && uv publish --token $(awk '/^\[pypi\]/,/^\[/' ~/.pypirc | grep password | sed 's/password = //')
```

### Workflow details
- Workflow file: `.github/workflows/publish.yml`
- Uses `uv build` + `uv publish` (not twine — twine 5.x/6.x can't handle metadata v2.4 from hatchling)
- Requires `PYPI_API_TOKEN` and `TEST_PYPI_API_TOKEN` repo secrets (API tokens from pypi.org, set via `gh secret set`)
- GitHub environment protection rules: `pypi` and `testpypi` environments

## Claude Desktop Configuration

### Recommended: uvx (Zero-Install)
**Simplest setup — no virtual environment management needed.**
`uvx` (from [uv](https://docs.astral.sh/uv/)) automatically creates an isolated environment, installs ragdex, and runs the MCP server. This is the standard pattern for Python MCP servers.

```json
{
  "mcpServers": {
    "personal-library": {
      "command": "uvx",
      "args": ["ragdex-mcp"],
      "env": {
        "MCP_WARMUP_ON_START": "true",
        "MCP_INIT_TIMEOUT": "30",
        "MCP_TOOL_TIMEOUT": "15"
      }
    }
  }
}
```

Install uv if not already available: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Alternative: pipx (Permanent Installation)
```bash
pipx install ragdex
```
```json
{
  "mcpServers": {
    "personal-library": {
      "command": "ragdex-mcp",
      "env": {
        "MCP_WARMUP_ON_START": "true"
      }
    }
  }
}
```

### Advanced: Manual venv (For Development/Contributors)
Use `uv pip install -e .` in a virtual environment for editable installs:

```json
{
  "mcpServers": {
    "personal-library": {
      "command": "/path/to/your/ragdex_env/bin/python",
      "args": ["-m", "personal_doc_library.servers.mcp_complete_server"],
      "env": {
        "PYTHONPATH": "/path/to/your/ragdex/src",
        "PYTHONUNBUFFERED": "1",
        "MCP_WARMUP_ON_START": "true",
        "MCP_INIT_TIMEOUT": "30",
        "MCP_TOOL_TIMEOUT": "15"
      }
    }
  }
}
```

## Development Guidelines

### Python Environment
- **Prefer `uv`** for all pip operations and running services
- Use `uv pip install -e .` for editable development installs
- Python 3.9+ required (3.11 recommended)

### Document Processing Pipeline
1. **Discovery**: Scan directory for supported formats (PDF, Word, EPUB, MOBI/AZW/AZW3)
2. **Hash Checking**: MD5 comparison for change detection
3. **Processing**: Document → Loader → Text Extraction → Chunking → Categorization → Embedding → Vector Storage
   - Large PDFs (>50MB) use incremental page-by-page extraction via `_load_pdf_with_progress()` with progress reporting every 100 pages
   - Timeouts are page-count-aware for PDFs (3s/page, capped at 4 hours) with adaptive extensions
4. **Error Handling**: Timeout protection, automatic PDF cleaning, failed document tracking, MOBI conversion via Calibre
5. **Skip/Retry**: Users can skip or retry failed documents via the web monitor UI or `ragdex-index --skip <rel_path>`

### Vector Storage Details
- **Model**: sentence-transformers/all-mpnet-base-v2 (768-dimensional)
- **Database**: ChromaDB with persistent storage
- **Chunking**: 1200 characters with 150 character overlap
- **Categories**: practice, energy_work, philosophy, general

### Large File and Long-Running Operation Guidelines

When working with document processing code, especially `shared_rag.py`:

1. **Never use file size alone for timeout budgets** — a 200MB PDF can have 50 pages or 40,000 pages. Always check content density (page count for PDFs) and adjust timeouts accordingly.
2. **Every long-running phase must emit progress** — if a phase takes more than 30 seconds, it must write to `indexing_progress.json` so the adaptive timeout loop can detect liveness and extend. A blocking call with no progress output will be killed by the watchdog.
3. **Use incremental processing for large files** — instead of loading an entire large document in one shot (`loader.load()`), process it incrementally (page-by-page for PDFs) to emit progress and enable timeout extensions.
4. **Scale max_extensions with file size** — small files need fewer extensions; large/dense files may need 10-20 extensions to complete embedding of hundreds of thousands of chunks.
5. **Test with the actual large file** — the Osho Books PDF (199MB, 39,883 pages, ~181K chunks) is the stress test. Any timeout or progress change should be verified against it.
6. **Web monitor must reflect actual state** — the `index_status.json` and `indexing_progress.json` can diverge (status says "idle" while progress shows active embedding). The web UI must check both and show the true state.

### Testing
- **No formal test suite exists** - high-priority contribution area
- **Manual testing**: Use `./scripts/run.sh` and monitoring tools
- Always test changes before committing

### Code Design Principles (SOLID)

When modifying or creating shell scripts, follow SOLID principles adapted for bash:

#### 1. Single Responsibility Principle (SRP)
**Each function should have ONE clear purpose**

✅ **Good Example**:
```bash
validate_executable() {
    local exe_path="$1"
    [ -x "$exe_path" ] && timeout 2 "$exe_path" --version &>/dev/null
}

check_port_available() {
    local port="$1"
    ! lsof -Pi ":$port" -sTCP:LISTEN -t >/dev/null 2>&1
}

create_directory_safe() {
    local dir_path="$1"
    mkdir -p "$dir_path" && touch "$dir_path/.test" && rm "$dir_path/.test"
}
```

❌ **Anti-pattern**:
```bash
# Violates SRP - does discovery, validation, and path setting
setup_everything() {
    find_ragdex
    validate_all
    create_all_dirs
    install_all_services
    # Too many responsibilities!
}
```

#### 2. Open/Closed Principle (OCP)
**Design for extension without modification**

✅ **Good Example**:
```bash
# Configuration-driven approach (easy to extend)
declare -A SERVICES=(
    ["indexer"]="com.ragdex.indexer:$RAGDEX_INDEX_PATH"
    ["webmonitor"]="com.ragdex.webmonitor:$RAGDEX_WEB_PATH"
)

install_service() {
    local service_name="$1"
    local service_config="${SERVICES[$service_name]}"
    # Generic installation logic
}

# Adding new service requires NO code changes, just config:
# SERVICES["newservice"]="com.ragdex.newservice:$RAGDEX_NEW_PATH"
```

❌ **Anti-pattern**:
```bash
# Hard-coded approach (requires modification to extend)
install_services() {
    install_indexer
    install_webmonitor
    # Adding new service requires editing this function
}
```

#### 3. Liskov Substitution Principle (LSP)
**Subtypes/variants should be interchangeable**

✅ **Good Example**:
```bash
# Generic interface for all validators
validate_resource() {
    local resource_type="$1"
    local resource_value="$2"

    case "$resource_type" in
        "executable") validate_executable "$resource_value" ;;
        "directory") validate_directory "$resource_value" ;;
        "port") validate_port "$resource_value" ;;
    esac
}

# All validators follow same contract: take value, return 0/1
```

#### 4. Interface Segregation Principle (ISP)
**Provide specific interfaces, not one generic one**

✅ **Good Example**:
```bash
# Specific validation functions
validate_paths() { ... }      # Only validates paths
validate_executables() { ... } # Only validates executables
validate_services() { ... }    # Only validates services

# Caller uses only what they need
validate_paths || exit 1
```

❌ **Anti-pattern**:
```bash
# Monolithic validation
validate_everything() {
    # Forces all callers to validate everything, even if they only need paths
}
```

#### 5. Dependency Inversion Principle (DIP)
**Depend on abstractions, not concrete implementations**

✅ **Good Example**:
```bash
# Abstract service manager interface
SERVICE_MANAGER="${SERVICE_MANAGER:-launchctl}"

load_service() {
    local plist="$1"
    case "$SERVICE_MANAGER" in
        launchctl) launchctl load "$plist" ;;
        systemctl) systemctl enable "$plist" ;;
        # Easy to add new service managers
    esac
}

# Configuration determines implementation
```

❌ **Anti-pattern**:
```bash
# Hard-coded dependency on launchctl
load_service() {
    launchctl load "$1"  # Can't use systemctl or other service managers
}
```

### Refactoring Guidelines

When enhancing existing scripts:

1. **Extract Functions** - Break large functions (>50 lines) into smaller, focused ones
2. **Use Configuration** - Replace hard-coded values with arrays/associative arrays
3. **Centralize Validation** - Create reusable validation functions
4. **Error Abstraction** - Use consistent error handling patterns
5. **Testability** - Write functions that can be tested independently

**Example Refactoring Pattern**:

Before (monolithic):
```bash
# setup_services.sh lines 71-100
# Mixed discovery, validation, and path setting
if command -v ragdex-mcp &> /dev/null; then
    RAGDEX_MCP_PATH=$(which ragdex-mcp)
    RAGDEX_INDEX_PATH=$(which ragdex-index)
    RAGDEX_WEB_PATH=$(which ragdex-web)
    echo "Found ragdex in PATH"
elif [ -f "$RAGDEX_ENV/bin/ragdex-mcp" ]; then
    # ... more logic
fi
```

After (SOLID-compliant):
```bash
# Separated concerns
discover_ragdex_installation() {
    local search_locations=("$PATH" "$RAGDEX_ENV/bin" "$PARENT_DIR/bin")
    for location in "${search_locations[@]}"; do
        find_executables_in "$location" && return 0
    done
    return 1
}

validate_discovered_executables() {
    for cmd in "ragdex-mcp" "ragdex-index" "ragdex-web"; do
        validate_executable "${cmd}_PATH" || return 1
    done
    return 0
}

# Main flow
discover_ragdex_installation || die "Ragdex not found"
validate_discovered_executables || die "Invalid installation"
```

### Script Organization Template

For new scripts, follow this structure:

```bash
#!/bin/bash
set -euo pipefail

# 1. Constants and Configuration
readonly SCRIPT_VERSION="1.0.0"
declare -A CONFIG=(...)

# 2. Utility Functions (generic, reusable)
die() { echo "$*" >&2; exit 1; }
log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

# 3. Validation Functions (SRP - one purpose each)
validate_executable() { ... }
validate_directory() { ... }
validate_port() { ... }

# 4. Business Logic Functions (SRP - specific tasks)
discover_installation() { ... }
create_configuration() { ... }
install_service() { ... }

# 5. Orchestration
main() {
    parse_arguments "$@"
    validate_environment
    discover_installation
    create_configuration
    install_services
    verify_installation
}

# 6. Entry Point
main "$@"
```

### Testing SOLID Code

SOLID-compliant code is easier to test:

```bash
# test_install_script.sh
source setup_services.sh

# Test individual functions (SRP makes this possible)
test_validate_executable() {
    # Mock executable
    touch /tmp/test_exe && chmod +x /tmp/test_exe

    if validate_executable "/tmp/test_exe"; then
        echo "✓ validate_executable works"
    else
        echo "✗ validate_executable failed"
        return 1
    fi
}

# Run tests
test_validate_executable
test_check_port_available
test_create_directory_safe
```

### When to Apply SOLID

**Always apply when**:
- Creating new scripts
- Major refactoring of existing scripts
- Scripts will be maintained long-term
- Scripts are >200 lines

**Consider trade-offs for**:
- Small utility scripts (<50 lines)
- One-time migration scripts
- Scripts that won't change often

### Key Takeaway

**SOLID principles make bash scripts**:
- ✅ Easier to test
- ✅ Easier to debug
- ✅ Easier to extend
- ✅ More maintainable
- ✅ More professional

**Apply these principles to all new scripts and when enhancing existing ones.**

### Library-Specific Coding Standards

#### ChromaDB
- **Batch size**: 50-150 is the sweet spot. Hard max per `add()` is ~5,461 embeddings. Never insert one vector at a time.
- **Use `upsert()`** instead of `add()` when documents may already exist (re-indexing scenarios).
- **Thread safety**: Thread-safe within a single process. For multi-process concurrent access, use HTTP Client/Server mode or file-based locking (current approach with `IndexLock` is correct).
- **Persistent client**: Use `chromadb.PersistentClient(path=...)` for single-process access.

#### LangChain (Deprecation Warnings — Must Fix Before v1.0)
The following imports are deprecated and will break on LangChain 1.0:

| Current (deprecated) | Replacement | Package to add |
|---|---|---|
| `langchain_community.embeddings.HuggingFaceEmbeddings` | `langchain_huggingface.HuggingFaceEmbeddings` | `langchain-huggingface` |
| `langchain_community.vectorstores.Chroma` | `langchain_chroma.Chroma` | `langchain-chroma` |
| `langchain.schema.Document` | `langchain_core.documents.Document` | `langchain-core` |
| `langchain.text_splitter.RecursiveCharacterTextSplitter` | `langchain_text_splitters.RecursiveCharacterTextSplitter` | `langchain-text-splitters` |

#### sentence-transformers
- **Load once, reuse everywhere** — model loading takes 15-20s and ~420MB memory. The singleton pattern in `SharedRAG.__init__()` is correct.
- **Always batch encode** — pass lists to `model.encode(texts, batch_size=32)`, never encode one-by-one in a loop.
- **Max sequence length**: `all-mpnet-base-v2` supports 384 tokens. Ensure chunk sizes from the splitter don't exceed this.
- **Thread safety**: `encode()` is thread-safe for read-only inference on a shared model instance.

#### pypdf
- **Use `pypdf` (lowercase), NOT `PyPDF2`** — PyPDF2 is fully deprecated. Remove `pypdf2` from dependencies.
- **Use `strict=False`** when creating `PdfReader` to handle mildly malformed PDFs.
- **Per-page error handling**: Wrap individual page extraction in try/except since single pages can fail while others succeed.

#### Flask (Web Monitor)
- **Use `jsonify()`** for all API responses.
- **Add JSON error handlers** for 404/500 instead of returning default HTML.
- **Never `debug=True` in production**.
- **Mutable globals need locks** — read-only module-level variables (DB_DIR, etc.) are safe.

#### MCP Server
- **Stdout discipline is critical**: Only JSON-RPC messages on stdout. All logs to stderr.
- **Consider FastMCP migration**: The `mcp` package (v1.7+) includes FastMCP with `@mcp.tool()` decorators that auto-generate schemas from type hints, reducing boilerplate ~5x.
- **Never block the main event loop** with synchronous operations; use background threads for RAG initialization.

#### watchdog (File System Monitoring)
- **Never do heavy processing in event handler callbacks** — queue events and process in a worker thread (current approach is correct).
- **Always design for duplicate events** — file systems fire multiple events per logical change.
- **Avoid `PollingObserver`** except for network filesystems; native observers (FSEvents on macOS) are much more efficient.

### Threading vs Async Decision

Use `threading` (not `asyncio`) for the current architecture because pypdf, sentence-transformers, and ChromaDB are all synchronous libraries. Use `ProcessPoolExecutor` only for CPU-bound PDF text extraction. Use `ThreadPoolExecutor` for I/O-bound file reading and ChromaDB writes. Prefer batching over threading: 100 texts in one `encode()` call is faster than 10 threads encoding 10 texts each.

## Known Issues and Solutions

### LaunchAgent Permissions (macOS)
- **Issue**: LaunchAgent services restricted by sandboxing
- **Solution**: Use shell script wrapper (`scripts/index_monitor_service.sh`)
- **Details**: See `docs/LAUNCHAGENT_PERMISSIONS_SOLUTION.md`

### Large File Indexing Timeouts (v0.3.8 regression)
- **Issue**: Page-dense PDFs (e.g., 199MB / 39,883 pages) hit the 900s timeout because timeout tiers are based solely on file size, not page count. The loading phase (`loader.load()`) emits no progress, so the adaptive timeout extension cannot detect activity and help.
- **Root cause**: A 199MB file falls into the `< 200MB` bucket (900s), but 40K pages need far more than 15 minutes.
- **Solution (v0.3.9)**: Three-pronged fix:
  1. **Page-count timeout boost**: After the size-based timeout, check PDF page count via `pypdf` and boost timeout to `page_count * 3` (capped at 4 hours).
  2. **Incremental PDF loading**: For PDFs >50MB, use `_load_pdf_with_progress()` which extracts pages one at a time via `pypdf`, writing progress every 100 pages so the adaptive timeout can extend.
  3. **Scaled max_extensions**: `>100MB` → 20 extensions, `>50MB` → 10, otherwise 5.
- **Lesson**: Timeout budgets must account for content density (page count), not just file size. Always ensure long-running operations emit progress so watchdog loops can detect liveness.

### Common Troubleshooting
- If indexing finds 0 documents, check CloudDocs permissions
- For "Empty content" errors, documents may need cleaning
- Stale locks automatically cleaned after 30 minutes

## Environment Variables

### Path Configuration
- `PERSONAL_LIBRARY_DOC_PATH` - Override books directory
- `PERSONAL_LIBRARY_DB_PATH` - Override database directory
- `PERSONAL_LIBRARY_LOGS_PATH` - Override logs directory

### MCP Server Performance Configuration
- `MCP_WARMUP_ON_START` - Pre-initialize RAG system on server start (default: false)
  - Set to `true` to avoid 15-20 second initialization delay on first tool call
  - Recommended for production use
  - Example: `"MCP_WARMUP_ON_START": "true"`

- `MCP_INIT_TIMEOUT` - Maximum seconds to wait for RAG initialization (default: 30)
  - Used during server startup warmup
  - Increase if embedding model loading is slow on your system
  - Example: `"MCP_INIT_TIMEOUT": "45"`

- `MCP_TOOL_TIMEOUT` - Maximum seconds to wait before failing tool calls (default: 15)
  - Used when RAG isn't yet initialized and tool is called
  - User gets friendly "still initializing" message if timeout is exceeded
  - Example: `"MCP_TOOL_TIMEOUT": "20"`

### Web Monitor Configuration
- `MONITOR_PORT` - Override web monitor port (default: 8888 for PyPI, 9999 for source)
  - Example: `"MONITOR_PORT": "7777"`

## Best Practices

1. **Always check existing code** before creating new files
2. **Prefer editing** existing files over creating new ones
3. **Use absolute paths** in all configurations
4. **Test before committing** - no commits until testing complete
5. **Follow existing patterns** - check neighboring files for conventions
6. **No documentation files** unless explicitly requested
- Always prefer using uv for pip for both installation and running the services