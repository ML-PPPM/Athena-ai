#!/usr/bin/env python3
"""Test script for file upload functionality."""

import sys
sys.path.append('.')

from streamlit_app import process_uploaded_file
import io

# Test text file processing
print("🧪 Testing File Processing Functions")
print("=" * 50)

# Test text file
text_content = "This is a test text file for the Athena AI file upload feature."
text_file = type('MockFile', (), {
    'name': 'test.txt',
    'type': 'text/plain',
    'size': len(text_content),
    'getvalue': lambda: text_content.encode('utf-8')
})()

display, ai_content = process_uploaded_file(text_file)
print("✅ Text File Test:")
print(f"Display: {display[:100]}...")
print(f"AI Content: {ai_content[:100]}...")
print()

# Test image file (mock)
image_data = b"mock image data"
image_file = type('MockFile', (), {
    'name': 'test.png',
    'type': 'image/png',
    'size': len(image_data),
    'getvalue': lambda: image_data
})()

display, ai_content = process_uploaded_file(image_file)
print("✅ Image File Test:")
print(f"Display: {display[:100]}...")
print(f"AI Content: {ai_content[:100]}...")
print()

print("🎯 File Processing Test Complete!")