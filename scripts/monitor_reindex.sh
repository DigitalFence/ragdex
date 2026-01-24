#!/bin/bash
# Monitor re-indexing progress

OUTPUT_FILE="/private/tmp/claude/-Users-KDP-ragdex/tasks/bd3cc33.output"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "No active re-indexing task found"
    exit 1
fi

echo "📊 Re-indexing Progress Monitor"
echo "================================"
echo ""

# Show processing status
echo "Current status:"
tail -100 "$OUTPUT_FILE" | grep -E "^\[|Processing:|  ✅|  ❌|Summary:|Successfully indexed|Failed:|Total chunks" | tail -20

echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

# Watch for new progress
tail -f "$OUTPUT_FILE" | grep --line-buffered -E "^\[|Processing:|  ✅|  ❌|Summary:|Successfully indexed|Failed:|Total chunks"
