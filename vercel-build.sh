#!/bin/bash
echo "Cleaning up..."
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov
rm -rf dist
rm -rf build
rm -rf *.egg-info

echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Build completed!" 