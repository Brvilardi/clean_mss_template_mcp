#!/bin/bash
# Build and deployment script for React frontend
# This script is called during CDK deployment to build the frontend

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting frontend build process...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 1
fi

# Check if amplify_outputs.json exists
if [ ! -f "$FRONTEND_DIR/amplify_outputs.json" ]; then
    echo -e "${YELLOW}Warning: amplify_outputs.json not found in frontend directory${NC}"
    echo -e "${YELLOW}Please run generate_amplify_config.py first or ensure the file exists${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found amplify_outputs.json${NC}"

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found in frontend directory${NC}"
    exit 1
fi

# Install dependencies
echo -e "${GREEN}Installing npm dependencies...${NC}"
if ! npm install; then
    echo -e "${RED}Error: npm install failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Build the frontend
echo -e "${GREEN}Building frontend...${NC}"
if ! npm run build; then
    echo -e "${RED}Error: npm run build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend build completed${NC}"

# Check if dist directory was created
if [ ! -d "dist" ]; then
    echo -e "${RED}Error: dist directory not found after build${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build artifacts ready in dist/ directory${NC}"
echo -e "${GREEN}Frontend build process completed successfully!${NC}"

exit 0
