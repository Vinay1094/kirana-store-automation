.PHONY: help install run-api demo clean

help:
	@echo "Kirana Store Automation - Makefile Commands"
	@echo ""
	@echo "make install    - Install all dependencies"
	@echo "make run-api    - Start FastAPI server"
	@echo "make demo       - Run demo script"
	@echo "make test       - Run tests (when implemented)"
	@echo "make clean      - Clean generated files"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "\nDependencies installed successfully!"
	@echo "\nNote: Make sure Tesseract OCR is installed on your system:"
	@echo "  - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
	@echo "  - macOS: brew install tesseract"
	@echo "  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"

run-api:
	@echo "Starting FastAPI server..."
	python app.py

demo:
	@echo "Running demo script..."
	python examples/demo.py

test:
	@echo "Running tests..."
	pytest tests/ -v

clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf .pytest_cache
	rm -rf *.pyc
	rm -rf data/*.db
	rm -rf invoices/*.pdf
	@echo "Cleanup complete!"
