'''Original OCR
from mistralai import Mistral
from thefuzz import fuzz, process


def OCR():
    #API KEYS
    try:
        API_KEY = "B5rxs68cwfwWWE7zo53BXvAdawUOBQzE"
        client = Mistral(api_key=API_KEY)
    except Exception:
        API_KEY = "bZj0t7jIrakrUNvcmz9JaB0AZLdAWRND"
        client = Mistral(api_key=API_KEY)
    except Exception:
        print("API Key not found.  Please check your API Key.")

    # Get input file names
    sheet_file_name = str(input("Enter Answer Sheet Name: "))
    answer_file_name = str(input("Enter Answer Key Name: "))

    # Upload the answer sheet and answer key to Mistral
    answer_sheet = upload_pdf = client.files.upload(
        file={
            "file_name": f"{sheet_file_name}.pdf",
            "content": open(f"{sheet_file_name}.pdf", 'rb')
        },
        purpose="ocr"
    )

    answer_key = upload_pdf = client.files.upload(
        file={
            "file_name": f"{answer_file_name}.pdf",
            "content": open(f"{answer_file_name}.pdf", 'rb')
        },
        purpose="ocr"
    )

    # Get signed URLs for both documents
    signed_url_sheet = client.files.get_signed_url(file_id=answer_sheet.id)
    signed_url_key = client.files.get_signed_url(file_id=answer_key.id)

    # Process the OCR for both documents
    ocr_response_sheet = client.ocr.process(
        model = "mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url_sheet.url
        }
    )

    ocr_response_key = client.ocr.process(
        model = "mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url_key.url
        }
    )

    # Print the OCR results
    print("\nOCR Results for Answer Sheet:")

    for page in ocr_response_sheet.pages:
        print(page.markdown)


    print("\nOCR Results for Answer Key:")

    for page in ocr_response_key.pages:
        print(page.markdown)

    similarity(ocr_response_sheet, ocr_response_key)

    return ocr_response_sheet, ocr_response_key


def similarity(ocr__sheet, ocr__key):
    #To check Similarly between Answer Sheet and Answer Key
    similarity = fuzz.token_sort_ratio(ocr__sheet, ocr__key)

    print(f"\nSimilarity between Answer Sheet and Answer Key: {similarity}%")

if __name__ == "__main__":
    OCR()
'''

import cv2
import numpy as np
from pdf2image import convert_from_path

# Convert PDF to image
def pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path)
    return np.array(images[0])  # First page

# Preprocess image
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary

# Detect horizontal lines with Hough Transform
def detect_horizontal_lines(binary_image):
    lines = cv2.HoughLinesP(binary_image, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    horizontal_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) < 5:  # Nearly horizontal
                horizontal_lines.append((y1 + y2) // 2)
    return sorted(horizontal_lines)

# Compute projection profile
def compute_projection_profile(binary_image):
    return np.sum(binary_image, axis=1)

# Find paragraph breaks
def find_paragraph_breaks(profile, horizontal_lines, min_gap=20):
    breaks = []
    prev_end = 0
    for i in range(1, len(horizontal_lines)):
        gap = horizontal_lines[i] - horizontal_lines[i-1]
        if gap > min_gap and np.mean(profile[horizontal_lines[i-1]:horizontal_lines[i]]) < 10:
            breaks.append((prev_end, horizontal_lines[i-1]))
            prev_end = horizontal_lines[i]
    breaks.append((prev_end, horizontal_lines[-1]))
    return breaks

# Extract paragraphs
def extract_paragraphs(image, breaks):
    paragraphs = []
    for start, end in breaks:
        if end - start > 10:  # Minimum height
            paragraphs.append(image[start:end, :])
    return paragraphs

# Main function
def process_page(pdf_path):
    image = pdf_to_image(pdf_path)
    binary = preprocess_image(image)
    horizontal_lines = detect_horizontal_lines(binary)
    profile = compute_projection_profile(binary)
    breaks = find_paragraph_breaks(profile, horizontal_lines)
    paragraphs = extract_paragraphs(image, breaks)
    for i, para in enumerate(paragraphs):
        cv2.imwrite(f"paragraph_{i+1}.png", para)
    return len(paragraphs)

# Run it
pdf_path = "Answers.pdf"
num_paragraphs = process_page(pdf_path)
print(f"Detected {num_paragraphs} paragraphs.")