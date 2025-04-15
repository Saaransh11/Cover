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

def detect_word_boxes(img):
    # Binarize and invert
    _, binary = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    word_boxes = []
    for stat in stats[1:]:  # skip background
        x, y, w, h, area = stat
        if area > 30:
            word_boxes.append((x, y, w, h))
    return word_boxes

def find_paragraph_gaps(img, word_boxes, min_gap_height=10):
    height, width = img.shape
    row_has_text = np.zeros((height,), dtype=bool)

    # Mark rows that are part of any word box
    for x, y, w, h in word_boxes:
        row_has_text[y:y+h] = True

    # Find continuous regions of empty rows
    empty_gaps = []
    start = None
    for y in range(height):
        if not row_has_text[y]:
            if start is None:
                start = y
        else:
            if start is not None:
                gap_height = y - start
                if gap_height >= min_gap_height:
                    empty_gaps.append((start, y))
                start = None
    return empty_gaps

def process_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found!")

    height, width = img.shape
    marked_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Step 1: Detect words
    word_boxes = detect_word_boxes(img)
    for (x, y, w, h) in word_boxes:
        cv2.rectangle(marked_img, (x, y), (x + w, y + h), (0, 255, 0), 1)

    # Step 2: Find paragraph gaps
    gaps = find_paragraph_gaps(img, word_boxes)
    for start, end in gaps:
        mid = (start + end) // 2
        cv2.line(marked_img, (0, mid), (width, mid), (0, 0, 255), 1)

    return marked_img, gaps

# Example usage
if __name__ == "__main__":
    input_path = "page.png"
    output_path = "clean_cut_output.png"

    result_img, gaps = process_image(input_path)
    cv2.imwrite(output_path, result_img)

    print(f"🧼 Clean cut saved to: {output_path}")
    print(f"📎 Found paragraph breaks at lines: {[ (s,e) for s,e in gaps ]}")
