#!/usr/bin/env bash

set -e

echo "==== Resetting pipeline outputs ===="

# Remove generated work directory
if [ -d "work" ]; then
    echo "Removing work/"
    rm -rf work
fi

# Remove processed data
if [ -d "data/processed" ]; then
    echo "Cleaning data/processed/"
    rm -rf data/processed/*
fi

# Remove run logs
if [ -d "runs" ]; then
    echo "Cleaning runs/"
    rm -rf runs/*
fi

# Remove Python cache files
echo "Removing __pycache__ and .pyc files"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Recreate empty folders (important for pipeline)
mkdir -p data/processed
mkdir -p runs

echo "==== Reset complete ===="