#!/bin/bash

# Test script for GFPGAN API
# Tests all endpoints and quota functionality

API_URL="${1:-http://localhost:8000}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          GFPGAN Free API - Test Suite                      ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "🎯 API URL: $API_URL"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0

# Test helper
run_test() {
    local name=$1
    local cmd=$2
    
    test_count=$((test_count + 1))
    echo -n "Test $test_count: $name... "
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
}

# ===== TESTS =====

echo "📋 Testing endpoints..."
echo ""

# 1. Health check
run_test "Health check" "curl -s $API_URL/health | grep -q status"

# 2. Stats endpoint
run_test "Stats endpoint" "curl -s $API_URL/stats | grep -q redis_connected"

# 3. Root endpoint
run_test "Root endpoint" "curl -s $API_URL/ | grep -q GFPGAN"

# 4. Docs available
run_test "API Docs" "curl -s $API_URL/docs | grep -q openapi"

echo ""
echo "📊 Testing image processing..."
echo ""

# Create test image if not exists
if [ ! -f test_image.jpg ]; then
    echo "Creating test image..."
    python3 << 'EOF'
from PIL import Image, ImageDraw
import os

# Create a simple test image with a face-like pattern
img = Image.new('RGB', (256, 256), color='white')
draw = ImageDraw.Draw(img)

# Draw simple face
draw.ellipse([50, 50, 206, 206], fill='beige', outline='black', width=2)
draw.ellipse([100, 100, 120, 130], fill='black')  # Left eye
draw.ellipse([170, 100, 190, 130], fill='black')  # Right eye
draw.line([130, 180, 150, 200], fill='black', width=3)  # Mouth

img.save('test_image.jpg', 'JPEG')
print("✅ Test image created")
EOF
fi

# 5. Enhance with scale 2
run_test "Enhance 2x" "curl -s -X POST '$API_URL/enhance?scale=2' -F 'file=@test_image.jpg' -o /tmp/test_out_2x.png && [ -f /tmp/test_out_2x.png ]"

# 6. Enhance with scale 4
run_test "Enhance 4x" "curl -s -X POST '$API_URL/enhance?scale=4' -F 'file=@test_image.jpg' -o /tmp/test_out_4x.png && [ -f /tmp/test_out_4x.png ]"

# 7. Invalid scale
run_test "Invalid scale error" "curl -s -X POST '$API_URL/enhance?scale=3' -F 'file=@test_image.jpg' | grep -q '400'"

# 8. Missing file
run_test "Missing file error" "curl -s -X POST '$API_URL/enhance?scale=2' | grep -q '422'"

echo ""
echo "🔐 Testing rate limiting..."
echo ""

# 9. Check quota headers
run_test "Quota headers" "curl -s -i -X POST '$API_URL/enhance?scale=2' -F 'file=@test_image.jpg' | grep -q 'X-Quota-Used'"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                      Test Summary                           ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Total Tests:  $test_count                                     ║"
echo "║  Passed:       ${GREEN}$pass_count${NC}                                      ║"
echo "║  Failed:       $((test_count - pass_count))                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"

if [ $pass_count -eq $test_count ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}\n"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}\n"
    exit 1
fi
