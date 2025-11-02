#!/bin/bash
# 运行 Cursor DOM Inspector 测试

echo "=========================================="
echo "  🚀 Running Cursor DOM Inspector"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"
echo ""

echo "▶️  Starting test..."
echo ""

node cursor-dom-inspector.js

echo ""
echo "=========================================="
echo "  📊 Test Results"
echo "=========================================="
echo ""

if [ -d "cursor_dom_output" ]; then
    echo "✅ Output directory created"
    echo ""
    echo "📄 Generated files:"
    ls -lh cursor_dom_output/
    echo ""
    
    # 显示分析结果摘要
    if ls cursor_dom_output/cursor_analysis_*.json 1> /dev/null 2>&1; then
        echo "📊 Analysis Summary:"
        latest_analysis=$(ls -t cursor_dom_output/cursor_analysis_*.json | head -1)
        echo "   File: $latest_analysis"
        echo "   Stats:"
        cat "$latest_analysis" | grep -A 10 '"stats"' | head -15
    fi
else
    echo "❌ Output directory not created"
fi

echo ""
echo "=========================================="
echo "  ✅ Done!"
echo "=========================================="

