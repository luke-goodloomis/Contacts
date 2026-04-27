#!/usr/bin/env python
"""
Verify OCR setup and test image processing capabilities
Run this to ensure everything is configured correctly
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} - Need 3.8+")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    packages = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'Uvicorn ASGI server',
        'pydantic': 'Pydantic data validation',
        'PIL': 'Pillow image processing',
        'pytesseract': 'Pytesseract OCR wrapper'
    }
    
    all_ok = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✓ {package:15} - {description}")
        except ImportError:
            print(f"✗ {package:15} - MISSING: pip install {package}")
            all_ok = False
    
    return all_ok

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    import shutil
    if shutil.which('tesseract'):
        import subprocess
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        version_line = result.stdout.split('\n')[0]
        print(f"✓ Tesseract OCR - {version_line}")
        return True
    else:
        print("✗ Tesseract OCR - NOT FOUND")
        print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def check_files():
    """Check if all required files exist"""
    files = {
        'main.py': 'FastAPI application',
        'ocr_processor.py': 'OCR processing module',
        'requirements.txt': 'Python dependencies',
        'templates/index.html': 'Web interface',
        'static/app.js': 'JavaScript logic',
        'static/style.css': 'Styling'
    }
    
    all_ok = True
    for filepath, description in files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filepath:30} - {description} ({size:,} bytes)")
        else:
            print(f"✗ {filepath:30} - MISSING")
            all_ok = False
    
    return all_ok

def test_ocr_import():
    """Test if OCR module can be imported"""
    try:
        from ocr_processor import OCRProcessor
        print("✓ OCR module imports successfully")
        return True
    except Exception as e:
        print(f"✗ OCR module import failed: {e}")
        return False

def main():
    print("=" * 70)
    print("  CONTACT MANAGER WITH OCR - SETUP VERIFICATION")
    print("=" * 70)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Tesseract OCR", check_tesseract),
        ("Required Files", check_files),
        ("OCR Module", test_ocr_import)
    ]
    
    print()
    results = {}
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 70)
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Error: {e}")
            results[name] = False
    
    print()
    print("=" * 70)
    
    all_passed = all(results.values())
    if all_passed:
        print("  ✓ ALL CHECKS PASSED - Ready to start!")
        print()
        print("  Next steps:")
        print("  1. Run: python main.py")
        print("  2. Open: http://localhost:8000")
        print("  3. Click '📸 Scan Card' to test OCR with an image")
    else:
        print("  ✗ SOME CHECKS FAILED - See above for details")
        print()
        print("  Common fixes:")
        print("  - Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check Python version: python --version")
    
    print("=" * 70)
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
