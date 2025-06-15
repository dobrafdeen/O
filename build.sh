#!/bin/bash

# تنظيف الملفات المؤقتة
echo "Cleaning up..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov
rm -rf dist
rm -rf build
rm -rf *.egg-info

# تثبيت المتطلبات
echo "Installing dependencies..."
python3.9 -m pip install -r requirements.txt

# تنظيف الملفات غير الضرورية
echo "Removing unnecessary files..."
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
rm -rf .git
rm -rf .github
rm -rf tests
rm -rf docs

echo "Build completed!" 