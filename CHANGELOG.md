# Changelog

All notable changes to the Spiritual Library MCP Server will be documented in this file.

## [0.4.0] - 2025-01-25 - Performance Optimizations and Optional Dependencies

### Added
- **Performance Timing Instrumentation**: Added detailed timing logs for all major indexing operations
  - Individual operation timing: chunking, metadata processing, embedding
  - Batch-level timing for embedding operations
  - Real-time chunks/sec metrics for performance monitoring
  - High-resolution timing using `time.perf_counter()`

### Changed
- **Optimized Content Categorization**: Significantly improved metadata processing performance
  - Replaced `any(word in content for word in [...])` with set intersection algorithm
  - Pre-computes keyword sets to avoid repeated allocations
  - Uses word tokenization for O(n+m) complexity vs O(n*m)
  - Caches `indexed_at` timestamp to eliminate redundant datetime calls
  - **Impact**: ~10-20% faster metadata processing for large documents

- **Removed Deprecated persist() Call**: Eliminated unnecessary manual persistence
  - ChromaDB 0.4.x+ auto-persists, making manual `vectorstore.persist()` redundant
  - Removed deprecated call that triggered warnings on every document
  - **Impact**: Major reduction in I/O overhead and disk writes

### Performance Improvements
- **Large File Indexing**: Verified successful processing of 500MB+ PDFs
  - Example: Yoga Vashista English_OCR.pdf (498.9MB, 1845 pages, 5927 chunks)
    - Chunking: 0.09s
    - Metadata: 0.08s
    - Embedding: 70.03s @ 84.6 chunks/sec
- **Memory Efficiency**: Maintains stable usage (5-9% of 12GB configured limit)
- **Processing Throughput**: Consistent rates across document types
  - Small files (<10 chunks): 30-60 chunks/sec
  - Large files (5000+ chunks): 80-85 chunks/sec
- **System Reliability**: Successfully indexes complex multi-author collections

### Changed - Optional Dependencies
- **LibreOffice Made Optional**: Legacy .doc file support now requires optional installation
  - Install with: `pip install 'ragdex[doc-support]'` (also requires LibreOffice on system)
  - Modern .docx files work without LibreOffice (uses python-docx)
  - Graceful fallback with informative error messages when .doc files are encountered
  - **Impact**: Reduced installation complexity and dependency footprint for users without legacy .doc files

### Technical Details
- Set-based categorization reduces keyword matching from O(n*m) to O(n+m)
- Batch processing logs provide granular performance insights
- Removed redundant ChromaDB persist warnings from logs
- All timing measurements use high-resolution performance counter
- Optional dependency groups: `[doc-support]` for legacy .doc files, `[services]` for daemon support
- Smart fallback: .docx uses Docx2txtLoader when UnstructuredWordDocumentLoader not available

## [0.3.1] - 2025-11-24

### Added
- **MCP Server Performance Optimization**:
  - Background thread initialization to prevent MCP protocol timeouts
  - `MCP_WARMUP_ON_START` environment variable for pre-initialization on server start
  - Configurable timeouts via `MCP_INIT_TIMEOUT` and `MCP_TOOL_TIMEOUT`
  - Graceful timeout handling with user-friendly messages
  - Enhanced `warmup` tool with better status reporting
- **Enhanced Installation Scripts**:
  - Interactive Python version selection (supports 3.9-3.13)
  - Automatic detection of Homebrew vs PATH Python installations
  - Clear labeling of Python installation sources with full paths
  - Improved service co-existence (source vs PyPI installations)
  - Configurable web monitor ports (9999 for source, 8888 for PyPI)

### Changed
- **Python Version Support**: Expanded to Python 3.9-3.13 (previously 3.10-3.13)
- **Installation Experience**: Interactive selection of Python versions with clear labels
- **Initialization Strategy**: RAG system now initializes in background thread
- **Default Behavior**: First tool call waits up to 15 seconds for initialization
- **Recommended Configuration**: Set `MCP_WARMUP_ON_START=true` for production use

### Fixed
- **MCP Server Crashes**: Resolved timeout issues during embedding model loading
- **First Tool Call Delays**: Eliminated 15-20 second delays with warmup configuration
- **Installation Script Errors**: Fixed sed errors caused by ANSI color codes in command substitution
- **Python Detection**: Filter out broken uv-managed Python installations

## [0.3.0] - 2025-01-23

### Added
- **Python 3.13 Support**: Full compatibility with Python 3.13.9
- **Modern Dependencies**:
  - ChromaDB upgraded to 1.3.5 (from 0.4.22)
  - LangChain upgraded to 0.3.27 (from 0.1.0)
  - NumPy upgraded to 2.3.5 (from <2.0)
  - sentence-transformers upgraded to 5.1.2 (from 2.2.2)
- **Enhanced Document Support**: `unstructured` and `pypandoc` moved to core dependencies for better EPUB/DOCX support

### Changed
- **Python Version Support**: Now supports Python 3.10-3.13 (previously 3.10-3.12)
- **Dependency Strategy**: Modern version constraints with better compatibility
- **Performance**: 10-15% faster execution on Python 3.13

### Fixed
- **EPUB/DOCX Processing**: Improved reliability by making `unstructured` a core dependency
- **ARM64 Compatibility**: Better support with ChromaDB 1.3.5
- **Vector Search**: Enhanced performance with updated ChromaDB

### Technical
- **Zero Code Changes Required**: Migration was entirely dependency-based
- **100% MCP Tool Compatibility**: All 17 tools tested and verified working
- **Production Tested**: Validated with 73-document library (4336+ chunks)
- **Search Performance**: Maintained excellent speed (<1s queries)
- **Indexing Performance**: ~13.4s per document average

### Migration Notes
- Existing installations will seamlessly upgrade to new dependencies
- Vector database remains compatible (no rebuilding required)
- Python 3.14 support blocked by upstream `onnxruntime` dependency (expected in 3-6 months)
- See [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) for comprehensive testing results

## [2.1.0] - 2025-07-05

### Added
- **New Content Tools**: 
  - `summarize_book` - Generate AI summaries of entire books
  - `extract_quotes` - Find notable quotes on specific topics  
  - `daily_reading` - Get themed passages for daily practice
  - `question_answer` - Ask direct questions about teachings
- **ARM64 Compatibility**: Full Apple Silicon support with dedicated `venv_mcp`
- **Lazy Initialization**: Fast MCP startup, RAG loads only when tools are used
- **Proper MCP Protocol Compliance**: Fixed initialization response format
- **Enhanced Error Handling**: Proper JSON-RPC error responses

### Fixed
- **Architecture Mismatch**: Resolved x86_64 vs ARM64 issues on Apple Silicon
- **Embedding Dimension Mismatch**: Restored original 768-dim `all-mpnet-base-v2` model
- **MCP Timeout Issues**: Lazy initialization prevents 6-second startup delay
- **Search Functionality**: Now returns actual results instead of 0 passages
- **Server Disconnection**: Proper protocol flow keeps connection alive

### Changed
- **Embedding Model**: Switched from `all-MiniLM-L6-v2` (384-dim) to `all-mpnet-base-v2` (768-dim)
- **Virtual Environment**: Using `venv_mcp` with Homebrew Python for ARM64 compatibility
- **MCP Server Structure**: Complete rewrite with lazy loading and proper protocol handling

### Technical
- **Python Environment**: ARM64-native Python 3.11 via Homebrew
- **Vector Database**: ChromaDB with 768-dimensional embeddings
- **Performance**: ~1.75s search latency, supports synthesis across multiple sources
- **Monitoring**: Real-time web dashboard and comprehensive logging

## [2.0.0] - 2025-07-04

### Added
- **Hybrid Architecture**: Support for automatic, background, and manual indexing modes
- **Background Monitor Service**: Continuous monitoring with LaunchAgent support
- **Web Monitoring Interface**: Real-time status dashboard at localhost:8888
- **Enhanced Lock System**: File-based locking with stale detection and auto-cleanup
- **Automatic PDF Cleaning**: Ghostscript-based cleaning for problematic PDFs
- **Service Mode**: Install as system service with auto-restart capabilities

### Enhanced
- **Shared RAG System**: Common functionality between MCP server and background monitor
- **Error Recovery**: Automatic handling of corrupted or malformed PDFs
- **Content Categorization**: Improved classification into practice, energy_work, philosophy, general
- **Statistics Tracking**: Detailed library statistics and indexing history

## [1.0.0] - 2025-07-03

### Initial Release
- **Basic MCP Server**: Core Model Context Protocol implementation
- **RAG System**: PDF indexing with ChromaDB vector storage
- **Search Functionality**: Semantic search across spiritual library
- **Claude Integration**: Direct integration with Claude Desktop
- **PDF Processing**: Automatic text extraction and chunking
- **Synthesis Capabilities**: AI-powered synthesis across multiple sources

### Core Tools
- `search` - Semantic search with optional synthesis
- `find_practices` - Find specific spiritual practices
- `compare_perspectives` - Compare perspectives across sources
- `library_stats` - Get library statistics and indexing status

### Technical Foundation
- **Vector Storage**: ChromaDB with sentence-transformers embeddings
- **LLM Integration**: Ollama with llama3.1:70b model
- **PDF Processing**: PyPDF2 with recursive text splitting
- **Content Organization**: Metadata-based categorization system