# PDF Receipt Generator

A Python application that generates multi-page PDF receipts by combining JPG images with reportlab.

## Project Structure

```
gen_pdf/
├── pdfgen_receipt.py          # Main PDF generation script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── image_resources/            # Directory for input JPG images (4 required)
├── tests/
│   └── test_pdfgen_receipt.py # Unit tests
└── htmlcov/                    # Coverage report (generated after running tests)
```

## Features

- Validates that exactly 4 JPG images are present in `image_resources/` directory
- Creates a 2-page PDF with 2 images per page
- Adds 1mm black borders around each image
- Generates detailed log files with timestamps
- Requires Python 3.9 or higher

## Requirements

- Python 3.9+
- `pytest` — Unit testing framework
- `reportlab` — PDF generation library
- `coverage` — Code coverage measurement (for coverage reports)

## Installation

### 1. Navigate to Project Directory

```bash
cd /Users/ajaneedissanayake/Documents/chandima/python_run/gen_pdf
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Check that all packages are installed:

```bash
pip list
```

You should see:
- `pytest`
- `reportlab`

## Running Unit Tests

### Run All Tests

```bash
python3 -m pytest tests/test_pdfgen_receipt.py -v
```

**Expected Output:**
```
tests/test_pdfgen_receipt.py::test_get_jpg_files_missing_dir PASSED
tests/test_pdfgen_receipt.py::test_get_jpg_files_wrong_count PASSED
tests/test_pdfgen_receipt.py::test_get_jpg_files_success PASSED
tests/test_pdfgen_receipt.py::test_add_image_with_border_calls_canvas_methods PASSED
tests/test_pdfgen_receipt.py::test_create_page_calls_line_and_add_image_with_border PASSED
tests/test_pdfgen_receipt.py::test_custom_formatter_formats_time PASSED
tests/test_pdfgen_receipt.py::test_write_custom_log_writes_file PASSED

====== 7 passed in 0.21s ======
```

### Run Specific Test

```bash
python3 -m pytest tests/test_pdfgen_receipt.py::test_get_jpg_files_success -v
```

### Run Tests Quietly

```bash
python3 -m pytest tests/test_pdfgen_receipt.py -q
```

## Coverage Report

### Install Coverage Tool (if not already installed)

```bash
pip install coverage
```

### Generate Coverage Report

#### Terminal Report

Run tests with coverage and display results in terminal:

```bash
python3 -m coverage run -m pytest tests/test_pdfgen_receipt.py -q
python3 -m coverage report -m
```

**Expected Output:**
```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
pdfgen_receipt.py                 92     24    74%   22-23, 122-148, 153-159
tests/test_pdfgen_receipt.py      79      0   100%
------------------------------------------------------------
TOTAL                            171     24    86%
```

#### HTML Report

Generate an interactive HTML coverage report:

```bash
python3 -m coverage html
```

Then open the report in your browser:

```bash
open htmlcov/index.html
```

Or on Linux:

```bash
xdg-open htmlcov/index.html
```

### Coverage Details

- **Overall Coverage: 86%**
- **pdfgen_receipt.py: 74%** — Missing lines are commented code and entry point
- **tests/test_pdfgen_receipt.py: 100%** — All test code is executed

## Running the Main Script

### Prerequisites

1. Place exactly 4 JPG images in the `image_resources/` directory:
   ```
   image_resources/
   ├── image1.jpg
   ├── image2.jpg
   ├── image3.jpg
   └── image4.jpg
   ```

2. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

### Execute

```bash
python3 pdfgen_receipt.py
```

### Output

- **PDF File**: `2026_q_receipt.pdf` (2-page document)
- **Log File**: `pdfgen_receipt.<timestamp>.log` (execution details)

The script will:
1. Validate 4 JPG images are present
2. Create a 2-page PDF with images and 1mm black borders
3. Log all operations with timestamps
4. Exit with a prompt to press ENTER

## Test Coverage

The unit tests cover the following functions:

| Test | Function | Coverage |
|------|----------|----------|
| `test_get_jpg_files_missing_dir` | `get_jpg_files()` | Error handling for missing directory |
| `test_get_jpg_files_wrong_count` | `get_jpg_files()` | Error handling for wrong image count |
| `test_get_jpg_files_success` | `get_jpg_files()` | Successful image list retrieval |
| `test_add_image_with_border_calls_canvas_methods` | `add_image_with_border()` | Canvas operations (draw, border, rect) |
| `test_create_page_calls_line_and_add_image_with_border` | `create_page()` | Page layout and image positioning |
| `test_custom_formatter_formats_time` | `CustomFormatter.formatTime()` | Log time formatting with milliseconds |
| `test_write_custom_log_writes_file` | `write_custom_log()` | Log file writing |

## Cleaning Workspace

### Remove Test Results and Reports

Clean up all generated test artifacts, coverage reports, and log files:

```bash
# Remove coverage database and HTML reports
rm -rf .coverage htmlcov/

# Remove pytest cache
rm -rf .pytest_cache/

# Remove generated log files from main script execution
rm -f pdfgen_receipt.*.log

# Remove generated PDF output (optional)
rm -f 2026_q_receipt.pdf
```

### Full Clean Command

Remove all generated files at once:

```bash
rm -rf .coverage htmlcov/ .pytest_cache/ pdfgen_receipt.*.log 2026_q_receipt.pdf
```

## Clean and Re-Run Tests

### Complete Workflow: Clean → Install → Test → Coverage

Execute all steps in sequence to ensure a fresh test run:

```bash
# Step 1: Clean workspace
echo "Cleaning workspace..."
rm -rf .coverage htmlcov/ .pytest_cache/ pdfgen_receipt.*.log 2026_q_receipt.pdf

# Step 2: Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Step 3: Run unit tests
echo "Running unit tests..."
python3 -m pytest tests/test_pdfgen_receipt.py -v

# Step 4: Generate coverage report (terminal)
echo "Generating coverage report..."
python3 -m coverage run -m pytest tests/test_pdfgen_receipt.py -q
python3 -m coverage report -m

# Step 5: Generate HTML coverage report
echo "Generating HTML coverage report..."
python3 -m coverage html
echo "Coverage report generated: htmlcov/index.html"
```

### One-Liner Quick Command

Run the complete workflow in a single command:

```bash
rm -rf .coverage htmlcov/ .pytest_cache/ pdfgen_receipt.*.log 2026_q_receipt.pdf && \
pip install -r requirements.txt && \
python3 -m pytest tests/test_pdfgen_receipt.py -v && \
python3 -m coverage run -m pytest tests/test_pdfgen_receipt.py -q && \
python3 -m coverage report -m && \
python3 -m coverage html && \
echo "✓ Workspace cleaned, tests passed, coverage report generated!"
```

### Step-by-Step Manual Process

If you prefer to run each step separately:

```bash
# Step 1: Clean
rm -rf .coverage htmlcov/ .pytest_cache/ pdfgen_receipt.*.log 2026_q_receipt.pdf

# Step 2: Install
pip install -r requirements.txt

# Step 3: Test
python3 -m pytest tests/test_pdfgen_receipt.py -v

# Step 4: Coverage
python3 -m coverage run -m pytest tests/test_pdfgen_receipt.py -q
python3 -m coverage report -m
python3 -m coverage html
```

## Quick Start Command

Run everything in one go (install dependencies, run tests, and generate coverage):

```bash
pip install -r requirements.txt && \
python3 -m coverage run -m pytest tests/test_pdfgen_receipt.py -q && \
python3 -m coverage report -m && \
python3 -m coverage html && \
echo "Coverage report generated: htmlcov/index.html"
```

## Troubleshooting

### `pytest: command not found`

Ensure pytest is installed:
```bash
pip install pytest
```

### `reportlab: No module named`

Ensure reportlab is installed:
```bash
pip install reportlab
```

### `Directory 'image_resources' not found`

Create the directory and add 4 JPG images:
```bash
mkdir -p image_resources
# Add 4 JPG files to image_resources/
```

### Virtual Environment Not Activated

On macOS/Linux:
```bash
source .venv/bin/activate
```

On Windows:
```bash
.venv\Scripts\activate
```

## Python Version

Verify Python version is 3.9 or higher:

```bash
python3 --version
```

## License

This project is part of the pdfgen repository.

## Author

Chandima PDF Generator Project
