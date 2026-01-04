import os
import sys
import logging
from pathlib import Path
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime


# Check if the Python version is at least 3.9
if sys.version_info < (3, 9):
    print("Error: This script requires Python 3.9 or higher.")
    sys.exit(1)

# Configuration constants
NUM_IMAGES_REQUIRED = 4
MARGIN = 15 * mm
IMAGE_WIDTH = 180 * mm
IMAGE_HEIGHT = 118 * mm
BORDER_THICKNESS = 1 * mm
BORDER_COLOR = "black"
PDF_OUTPUT_FILE = "2026_q_receipt.pdf"
IMAGE_DIRECTORY = "image_resources"


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        if datefmt:
            s = datetime.fromtimestamp(record.created).strftime(datefmt)
            return f"{s}.{int(record.msecs):03d}"
        else:
            t = datetime.fromtimestamp(record.created)
            return t.strftime("%Y-%m-%d %H:%M:%S") + f".{int(record.msecs):03d}"


# Custom function to write plain text to the log file
def write_custom_log(message):
    with open(log_file_name, 'a') as log_file:
        log_file.write(message + '\n')


# Generate log file name
script_name = os.path.basename(__file__).split('.')[0]
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file_name = f"{script_name}.{current_time}.log"

# Configure logging
handler = logging.FileHandler(log_file_name)
formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class PDFGenerationError(Exception):
    """Base exception for PDF generation errors."""
    pass


class ImageNotFoundError(PDFGenerationError):
    """Raised when required images are not found or directory missing."""
    pass


def get_jpg_files(dir_name: str) -> List[str]:
    """Return list of jpg filenames in `dir_name`.

    Raises ImageNotFoundError when directory is missing or required count not met.
    """
    p = Path(dir_name)
    if not p.exists() or not p.is_dir():
        logging.error(f"Dir {dir_name} NOT FOUND.. ")
        raise ImageNotFoundError(f"Directory {dir_name} not found")

    logging.info(f"Dir found - {dir_name} ")
    jpg_files = [f.name for f in p.iterdir() if f.is_file() and f.name.lower().endswith('.jpg')]

    logging.info("Found images - {}".format(' | '.join(jpg_files)))
    if len(jpg_files) != NUM_IMAGES_REQUIRED:
        logging.error(f"Required image file count NOT FOUND.. Required {NUM_IMAGES_REQUIRED} / Found {len(jpg_files)}")
        raise ImageNotFoundError(f"{dir_name} does not contain the required number ({NUM_IMAGES_REQUIRED}) of images")

    logging.info("Images (4) found")
    return jpg_files


# Function to add an image with a border to the canvas
def add_image_with_border(c: canvas.Canvas, image_path: str, x: float, y: float, width: float, height: float) -> None:
    """Draw an image at given coords with a border on the provided canvas."""
    logging.info(f"Add image '{image_path}'")
    logging.info(f"Draw Image - '{image_path}' in X - {x} Y - {y} width - {width} height - {height}")
    c.drawImage(image_path, x, y, width=width, height=height)

    c.setLineWidth(BORDER_THICKNESS)
    c.setStrokeColor(BORDER_COLOR)
    logging.info(f"Draw Border thickness - {BORDER_THICKNESS} color - '{BORDER_COLOR}' in X - {x} Y - {y} "
                 f"width - {width} height - {height}")
    c.rect(x, y, width, height)


# Function to create a page with two images
def create_page(c: canvas.Canvas, image1_path: str, image2_path: str) -> None:
    """Create a single page containing two images separated by a horizontal line."""
    width, height = A4

    logging.info(f"Page Properties :- Margin - {MARGIN} / Width - {width} / Height - {height}")
    logging.info(f"Draw Line in X1 - {0} Y1 - {height / 2} X2 - {width} Y2 - {height / 2}")
    c.line(0, height / 2, width, height / 2)

    add_image_with_border(c, image1_path, MARGIN, (height / 2) + MARGIN, IMAGE_WIDTH, IMAGE_HEIGHT)
    add_image_with_border(c, image2_path, MARGIN, MARGIN, IMAGE_WIDTH, IMAGE_HEIGHT)


# Main function to create the PDF
def main(image_dir: str = IMAGE_DIRECTORY, output_file: str = PDF_OUTPUT_FILE) -> None:
    """Create the PDF from images in `image_dir` and write to `output_file`."""
    logging.info(f"Dir name - {image_dir}")
    jpg_files = get_jpg_files(image_dir)

    logging.info(f"PDF file name - {output_file}")
    c = canvas.Canvas(output_file, pagesize=A4)

    image_pairs = [
        (jpg_files[0], jpg_files[1]),
        (jpg_files[2], jpg_files[3]),
    ]

    for idx, (img1, img2) in enumerate(image_pairs, start=1):
        logging.info(f"creating page {idx}")
        create_page(c, str(Path(image_dir) / img1), str(Path(image_dir) / img2))
        if idx < len(image_pairs):
            c.showPage()
            logging.info("new page added")

    c.save()
    logging.info(f"'{output_file}' created")


# Entry point function to make testing possible
def run_pdf_generator():
    """Main entry point that can be tested."""
    write_custom_log(f"============================================================= Starting {log_file_name} "
                     f"=============================================================")
    main()
    write_custom_log(f"============================================================= Completed {log_file_name} "
                     f"=============================================================")
    print("File generated successfuly.. press ENTER to exit")
    k = input()


# Run the main function
if __name__ == "__main__":
    run_pdf_generator()
