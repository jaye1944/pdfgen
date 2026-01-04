import os
import sys
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

'''
width, height = A4

# Define margins, image dimensions, and border thickness
margin = 15 * mm
image_width = 180 * mm
image_height = 118 * mm
border = 1 * mm
'''

# Check if the Python version is at least 3.9
if sys.version_info < (3, 9):
    print("Error: This script requires Python 3.9 or higher.")
    sys.exit(1)


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

# Function to get JPG files from a directory
def get_jpg_files(dir_name):
    num_of_images = 4
    files = []
    try:
        # List all files in the directory
        files = os.listdir(dir_name)
    except FileNotFoundError:
        # Print error message and exit if directory not found
        print(f"{dir_name} not found")
        logging.error(f"Dir {dir_name} NOT FOUND.. ")
        exit(1)
    
    # Filter out JPG files
    logging.info(f"Dir found - {dir_name} ")
    jpg_files = [file for file in files if file.lower().endswith('.jpg')]

    logging.info("Found images - {}".format(' | '.join(jpg_files)))
    # Check if the number of JPG files is exactly 4
    if len(jpg_files) != num_of_images:
        print(f"{dir_name} does not contain the required number (4) of images")
        logging.error(f"Required image file count NOT FOUND.. Required {num_of_images} / Found {len(jpg_files)}")
        exit(1)
    logging.info("Images (4) found")
    return jpg_files


# Function to add an image with a border to the canvas
def add_image_with_border(c, image_path, x, y, width, height):
    border_thickness = 1 * mm
    border_color = "black"

    print(f"Add image '{image_path}'")
    logging.info(f"Draw Image - '{image_path}' in X - {x} Y - {y} width - {width} height - {height}")
    c.drawImage(image_path, x, y, width=width, height=height)

    c.setLineWidth(border_thickness)
    c.setStrokeColor(border_color)
    logging.info(f"Draw Border thickness - {border_thickness} color - '{border_color}' in X - {x} Y - {y} "
                 f"width - {width} height - {height}")
    c.rect(x, y, width, height)


# Function to create a page with two images
def create_page(c, image1_path, image2_path):
    width, height = A4

    # Define margins, image dimensions, and border thickness
    margin = 15 * mm
    image_width = 180 * mm
    image_height = 118 * mm

    logging.info(f"Page Properties :- Margin - {margin} / Width - {width} / Height - {height}")
    # Draw a line in the middle of the page
    logging.info(f"Draw Line in X1 - {0} Y1 - {height / 2} X2 - {width} Y2 - {height / 2}")
    c.line(0, height / 2, width, height / 2)

    # Add the first image to the top half of the page
    add_image_with_border(c, image1_path, margin, (height / 2) + margin, image_width, image_height)

    # Add the second image to the bottom half of the page
    add_image_with_border(c, image2_path, margin, margin, image_width, image_height)


# Main function to create the PDF
def main():
    dir_name = "image_resources"
    logging.info(f"Dir name - {dir_name}")
    jpg_files = get_jpg_files(dir_name)

    pdf_file = "2026_q_receipt.pdf"
    logging.info(f"PDF file name - {pdf_file}")
    c = canvas.Canvas(pdf_file, pagesize=A4)

    # Create the first page with the first two images
    print("creating page 1")
    logging.info("creating page 1")
    create_page(c, os.path.join(dir_name, jpg_files[0]), os.path.join(dir_name, jpg_files[1]))

    # Add a new page to the PDF
    c.showPage()
    logging.info("new page added")

    # Create the second page with the next two images
    print("creating page 2")
    logging.info("creating page 2")
    create_page(c, os.path.join(dir_name, jpg_files[2]), os.path.join(dir_name, jpg_files[3]))

    # Save the PDF file
    c.save()
    print(f"PDF file '{pdf_file}' has been created with two pages and resized "
          f"images(4) with borders(1 mm - black).")
    logging.info(f"'{pdf_file}' created")


# Run the main function
if __name__ == "__main__":
    write_custom_log(f"============================================================= Starting {log_file_name} "
                     f"=============================================================")
    main()
    write_custom_log(f"============================================================= Completed {log_file_name} "
                     f"=============================================================")
    print("File generated successfuly.. press ENTER to exit")
    k = input()
