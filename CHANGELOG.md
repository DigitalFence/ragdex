# Changelog

All notable changes to the Spiritual Library MCP Server will be documented in this file.

## [0.3.8] - 2026-02-24 - Indexer Stability and Web Retry Fixes

### Fixed
- **Web Retry Now Triggers Indexer**: Clicking retry on the web monitor now touches the document file (`os.utime`) to trigger the filesystem watcher, so the indexer automatically picks up retried documents without manual intervention.
- **Duplicate/Circular Processing**: Fixed race condition where the same documents were processed 4-9 times concurrently. Added `_processing_files` set with thread-safe locking to deduplicate across overlapping `process_pending_updates` calls.
- **Progress Display Overflow**: Fixed "Progress: 20/8 (250%)" bug where `current_document_index` accumulated across batches. Now resets to 0 at the start of each batch.
- **False Stale Lock Warning**: Removed 2-minute age-based stale lock threshold. Long embedding operations (30+ minutes) are normal; only dead-process detection is used now.
- **Timer Batching Delay**: `schedule_update()` no longer resets the timer on each filesystem event. Rapid events (e.g. multiple retry clicks) are batched into the next already-scheduled run instead of pushing the timer out indefinitely.
- **Indexer Crash on Restart**: Added missing `import sys` — `signal_handler` called `sys.exit(0)` but `sys` was not imported, causing a `NameError` crash on SIGTERM.
- **Silent Thread Exceptions**: Wrapped `process_pending_updates` in try/except with `exc_info` logging so exceptions in `threading.Timer` threads are no longer silently swallowed.

### Enhanced
- **Post-Processing Re-scheduling**: After finishing a batch, the indexer checks for events that arrived during processing and schedules another run automatically.

## [0.3.7] - 2026-02-24 - LaunchAgent PATH Fix, --retry Flag, Doc Fixes

### Fixed
- **LaunchAgent PATH**: macOS LaunchAgent services now include Homebrew paths (`/opt/homebrew/bin`, `/usr/local/bin`) in their environment. Previously, services ran with a minimal PATH that excluded tools like `soffice` (LibreOffice), `ebook-convert` (Calibre), and `gs` (Ghostscript), causing `.doc` and other format processing to fail.
- **Web Monitor Retry Route**: Fixed retry button failing for books with slashes in their path (e.g., `Osho/Rasik/...`). Flask route changed from `<book_name>` to `<path:book_name>` to match full paths.
- **CLI prog name**: Fixed `ragdex --help` displaying as `pdlib-cli` instead of `ragdex`.

### Added
- **`ragdex-index --retry` flag**: Clears the failed documents list (`failed_pdfs.json`) before starting the monitor, so all previously failed documents are re-attempted on the next sync cycle. Useful after installing missing tools like LibreOffice or Ghostscript.
- **`ragdex --version` / `-V` flag**: Shows the installed ragdex version using package metadata.

### Documentation
- Removed references to non-existent `document-processing` pip extra; corrected to `doc-support`
- Removed poppler-utils from optional dependencies (not used; ragdex uses pypdf and pdfminer.six)
- Added Ghostscript as documented optional dependency for cleaning corrupted PDFs
- Clarified that OCR requires both ocrmypdf and Tesseract, with auto-detection details
- Marked Linux support as untested throughout all guides
- Added "install all optional tools at once" convenience block to QUICKSTART.md
- Added optional system dependencies table to QUICK_REFERENCE.md

## [0.3.6] - 2025-01-25 - Bug Fixes, Subfolder Search, and Pagination

### Fixed
- **book_pages Tool**: Fixed ChromaDB API error caused by invalid 'ids' parameter in include list
  - Error: `Expected include item to be one of documents, embeddings, metadatas, distances, uris, data, got ids`
  - Solution: Removed 'ids' from include parameter, use metadatas for count calculation
  - **Impact**: book_pages tool now works correctly to retrieve page information

- **Search Validation**: Fixed crashes when documents have None or empty page_content
  - Added validation to skip invalid documents during search result processing
  - Prevents `1 validation error for Document page_content` exceptions
  - **Impact**: Search operations more robust against corrupted/malformed documents

- **extract_pages Tool**: Enhanced flexibility and reliability
  - Now accepts string page numbers (e.g., "0", "5", "10-15") in addition to integers
  - Automatically falls back to chunk extraction when page numbers unavailable
  - Properly handles single-page PDFs and resume documents indexed without page metadata
  - **Impact**: Resume PDFs and documents without page numbers now extractable

### Added
- **Subfolder Search Filtering**: New `folder` parameter for search tool
  - Filter searches by folder path (e.g., "DigitalFence", "DigitalFence/OU students resumes")
  - Supports partial folder matching (case-insensitive substring match)
  - Post-processing implementation for ChromaDB compatibility
  - **Usage**: `search(query="...", folder="DigitalFence")`
  - **Note**: Requires re-indexing existing documents to use this feature

- **Pagination Support for list_books**: New `offset` parameter for paginating large result sets
  - Navigate through results in pages (e.g., offset=0 for page 1, offset=50 for page 2)
  - Limit capped at 200 books per page for performance
  - Intelligent pagination hints show next page command
  - **Usage**: `list_books(pattern="...", limit=100, offset=0)`
  - **Impact**: Can now browse through libraries with 100+ books efficiently

### Enhanced
- **Document Metadata**: Added new metadata fields during indexing
  - `folder`: Directory path relative to library root (e.g., "DigitalFence/OU students resumes")
  - `rel_path`: Full relative path including filename
  - **Impact**: Enables folder-based filtering and better document organization

### Technical Details
- ChromaDB post-processing filter for folder search (workaround for missing $contains operator)
- Intelligent fallback strategy: page-based extraction → chunk-based extraction
- String page number parsing with range support ("1", "5", "10-15")
- Backward compatible with existing indexed documents (folder search unavailable until re-indexed)

### Migration Notes
- **Re-indexing Required**: Existing documents need re-indexing to use folder search
  - New documents: Automatically get folder metadata during indexing
  - Existing documents: Will continue to work but won't have folder metadata
  - Full re-index: `rm -rf chroma_db/* && re-index all documents`
- **MCP Server Restart**: Restart Claude Desktop to load updated code

## [0.3.5] - 2025-01-25 - Fix refresh_cache Command

### Fixed
- **refresh_cache Tool**: Fixed critical bug where newly indexed documents didn't appear in searches
  - Previously: `load_book_index()` result was not assigned, leaving stale data in memory
  - Previously: Vector store was never reloaded, so new documents remained invisible
  - Now: Properly reloads book index, vector store, and clears all caches
  - **Impact**: Users can now see newly indexed documents without restarting the MCP server

### Enhanced
- **Cache Management**: refresh_cache now clears all caches comprehensively
  - Reloads book index from disk
  - Reloads vector store to pick up new documents
  - Clears search cache (5-minute TTL cache)
  - Clears category cache (5-minute TTL cache, introduced in v0.3.4)
  - Provides detailed feedback on what was refreshed

### Technical Details
- Fixed assignment: `self.rag.book_index = self.rag.load_book_index()`
- Added vector store reload: `self.rag.vectorstore = self.rag.initialize_vectorstore()`
- Backward compatible: Safely handles missing `_category_cache` attribute
- Originally reported in PR #4

## [0.3.4] - 2025-01-25 - MCP Server Query Performance

### Added
- **MCP Query Caching**: Implemented 5-minute cache for `library_stats` category counts
  - First call: ~48 seconds (fetches 675K+ documents)
  - Subsequent calls: <1 second (cached)
  - Cache automatically expires after 5 minutes
  - **Impact**: 48× faster for repeated library_stats calls

### Performance Improvements
- **MCP Server Response Time**: Dramatically improved for repeated queries
  - `library_stats` tool: 48s → <1s for cached calls
  - Eliminates slowness when using MCP tools in quick succession
  - Ideal for interactive use with Claude Desktop

### Technical Details
- Category counts cached in memory with 5-minute TTL
- Automatic cache invalidation ensures fresh data
- Cache stored per-instance (SharedRAG singleton pattern)

## [0.3.3] - 2025-01-25 - Performance Optimizations and Optional Dependencies

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