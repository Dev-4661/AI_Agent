import pytesseract
from PIL import Image
import os
import sys

def extract_text_from_image(image_path):
    """
    Extract text from an image file using OCR.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Open the image file
        img = Image.open(image_path)
        
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(img)
        
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    # Get the path to the image from user input
    image_path = input("Enter the path to the image file: ")
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print("Error: The specified file does not exist.")
        
    
    # Extract text from the image
    extracted_text = extract_text_from_image(image_path)
    
    # Print the extracted text
    print("\nExtracted Text:")
    print("-" * 50)
    print(extracted_text)
    print("-" * 50)

if __name__ == "__main__":
    # Check if pytesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract OCR is not installed or not in your system's PATH.")
        print("Please follow these steps to install Tesseract OCR:")
        print("1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Run the installer")
        print("3. During installation, make sure to check the option to 'Add to PATH'")
        print("4. Restart your terminal/IDE after installation")
        sys.exit(1)
    
    main()
