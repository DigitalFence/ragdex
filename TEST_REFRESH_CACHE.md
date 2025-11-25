# Test Procedure: refresh_cache Fix (v0.3.5)

This document provides step-by-step instructions to verify that the `refresh_cache` tool correctly picks up newly indexed documents.

## Bug Being Tested

**Previous Behavior**: After indexing new documents, the `refresh_cache` tool would not make them visible in searches. Users had to restart the MCP server.

**Expected Fix**: After calling `refresh_cache`, newly indexed documents should immediately be searchable.

---

## Prerequisites

1. Claude Desktop is installed and configured with the Personal Library MCP server
2. You have access to `/Users/hpoliset/SpiritualLibrary` (your document directory)
3. You have a test document ready (or will create one)

---

## Test Procedure

### Phase 1: Preparation

#### Step 1.1: Create a Test Document

Create a simple text file with unique, searchable content:

```bash
cat > /Users/hpoliset/SpiritualLibrary/TEST_REFRESH_CACHE_$(date +%Y%m%d_%H%M%S).txt << 'EOF'
REFRESH CACHE TEST DOCUMENT

This is a test document to verify the refresh_cache functionality.

Unique test phrase: XYZZY_MAGIC_REFRESH_TEST_12345

This document should become searchable after calling refresh_cache
without requiring an MCP server restart.

Test timestamp: $(date)
EOF
```

**Expected Result**: File created successfully in your library directory.

#### Step 1.2: Note Current Library State

Open Claude Desktop and ask:
```
Use the library_stats tool to show me my current library statistics
```

**Record the following**:
- Total books: ________
- Total chunks: ________
- General chunks: ________

---

### Phase 2: Index the Test Document

#### Step 2.1: Index Using Background Monitor

**Option A: If background monitor is running**
```bash
# Wait 30-60 seconds for automatic indexing
# Check logs:
tail -f /Users/hpoliset/AITools/logs/index_monitor.log
```

**Option B: Manual indexing (recommended for controlled testing)**
```bash
export PYTHONPATH="/Users/hpoliset/AITools/src"
./venv_mcp/bin/python -m personal_doc_library.indexing.index_documents \
  --doc-path "/Users/hpoliset/SpiritualLibrary"
```

**Expected Result**:
- Log shows "Processing: TEST_REFRESH_CACHE_*.txt"
- Log shows "Successfully indexed: TEST_REFRESH_CACHE_*.txt"
- No errors in logs

#### Step 2.2: Verify Document is Indexed on Disk

Check that the book index was updated:

```bash
# Check if the test file appears in book_index.json
grep -i "TEST_REFRESH_CACHE" /Users/hpoliset/AITools/chroma_db/book_index.json
```

**Expected Result**: Should show an entry for your test document.

---

### Phase 3: Test BEFORE refresh_cache (Demonstrate the Bug)

#### Step 3.1: Try Searching for New Document

In Claude Desktop, ask:
```
Search my library for "XYZZY_MAGIC_REFRESH_TEST_12345"
```

**Expected Result (BUG BEHAVIOR)**:
- ❌ No results found
- This proves the document is indexed on disk but not loaded in the MCP server's memory

#### Step 3.2: Check Library Stats Again

In Claude Desktop, ask:
```
Use library_stats to show my current statistics
```

**Expected Result (BUG BEHAVIOR)**:
- Total books: ________ (SAME as Step 1.2 - no change)
- Total chunks: ________ (SAME as Step 1.2 - no change)
- This proves the MCP server is using stale cached data

---

### Phase 4: Test refresh_cache (The Fix)

#### Step 4.1: Call refresh_cache Tool

In Claude Desktop, ask:
```
Use the refresh_cache tool to reload the library
```

**Expected Result (FIX WORKING)**:
```
✅ Cache refreshed successfully!

📚 Total books: [NEW COUNT - should be +1]
📊 Total chunks: [NEW COUNT - should be higher]
🔄 Vector store: Reloaded
🗑️  Search cache: Cleared
🗑️  Category cache: Cleared
```

**Verify**:
- ✅ Message shows "Vector store: Reloaded"
- ✅ Message shows "Search cache: Cleared"
- ✅ Message shows "Category cache: Cleared"
- ✅ Book count increased by 1
- ✅ Chunk count increased

---

### Phase 5: Test AFTER refresh_cache (Verify the Fix)

#### Step 5.1: Search Again

In Claude Desktop, ask the same query:
```
Search my library for "XYZZY_MAGIC_REFRESH_TEST_12345"
```

**Expected Result (FIX WORKING)**:
- ✅ Document NOW found!
- ✅ Results show passages containing "XYZZY_MAGIC_REFRESH_TEST_12345"
- ✅ Source shows "TEST_REFRESH_CACHE_*.txt"

#### Step 5.2: Verify Library Stats Updated

In Claude Desktop, ask:
```
Use library_stats again to confirm the new book is counted
```

**Expected Result (FIX WORKING)**:
- ✅ Total books: [Matches the count from Step 4.1]
- ✅ Total chunks: [Matches the count from Step 4.1]
- ✅ New document is now included in the statistics

#### Step 5.3: Test Category Cache Clearing

In Claude Desktop, ask:
```
Use library_stats twice in a row and show me the response times
```

**Expected Result (FIX WORKING)**:
- First call: ~2-48 seconds (cache miss - normal)
- Second call: <1 second (cache hit - proves category cache is working)
- This proves the category cache was properly cleared and rebuilt

---

### Phase 6: Cleanup

#### Step 6.1: Remove Test Document

```bash
# Find and remove test document
rm /Users/hpoliset/SpiritualLibrary/TEST_REFRESH_CACHE_*.txt
```

#### Step 6.2: Refresh Cache Again

In Claude Desktop:
```
Use refresh_cache to remove the test document from the index
```

**Expected Result**:
- Book count should decrease by 1
- Chunk count should decrease accordingly

---

## Test Results Summary

Fill out this checklist:

### Bug Demonstration (Phase 3)
- [ ] ❌ Search before refresh_cache: Document NOT found (bug confirmed)
- [ ] ❌ Stats before refresh_cache: Old counts shown (bug confirmed)

### Fix Verification (Phase 4 & 5)
- [ ] ✅ refresh_cache shows all clear messages
- [ ] ✅ Search after refresh_cache: Document FOUND
- [ ] ✅ Stats after refresh_cache: New counts shown
- [ ] ✅ Category cache properly cleared and rebuilt

### Overall Result
- [ ] **PASS** - All tests passed, fix is working correctly
- [ ] **FAIL** - Some tests failed (document issues below)

---

## Troubleshooting

### Issue: Test document not indexed
**Solution**:
```bash
# Manually trigger indexing
export PYTHONPATH="/Users/hpoliset/AITools/src"
./venv_mcp/bin/python -m personal_doc_library.indexing.index_documents \
  --doc-path "/Users/hpoliset/SpiritualLibrary" --force
```

### Issue: refresh_cache doesn't show new messages
**Problem**: You might be running the old code version
**Solution**:
```bash
# Verify you're on the latest commit
git log --oneline -1
# Should show: "fix: Properly reload all caches in refresh_cache tool (v0.3.5)"

# Restart Claude Desktop to pick up the new code
```

### Issue: MCP server not responding
**Solution**:
```bash
# Check MCP logs
tail -50 ~/Library/Logs/Claude/mcp-server-Personal\ Library.log

# Restart Claude Desktop completely
```

---

## Notes

- This test creates minimal overhead (one small text file)
- Test can be repeated multiple times safely
- The test document is deliberately simple to ensure fast indexing
- Always clean up test documents after testing

---

## Sign-off

Tested by: ________________
Date: ________________
Result: ☐ PASS  ☐ FAIL
Notes: ________________________________________________________________
