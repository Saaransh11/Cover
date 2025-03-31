''' Original Code for OCR
API_KEY = "bZj0t7jIrakrUNvcmz9JaB0AZLdAWRND"
from mistralai import Mistral

client = Mistral(api_key=API_KEY)
file_name = str(input("Enter File Name: "))

upload_pdf = client.files.upload(
    file={
        "file_name": f"{file_name}.pdf",
        "content": open(f"{file_name}.pdf", 'rb')
    },
    purpose="ocr"
)

signed_url = client.files.get_signed_url(file_id=upload_pdf.id)

ocr_response = client.ocr.process(
    model = "mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": signed_url.url
    }
)


for page in ocr_response.pages:
    print(page.markdown)'
'''
'''OCR With JPEG
API_KEY = "bZj0t7jIrakrUNvcmz9JaB0AZLdAWRND"
from mistralai import Mistral
import base64

def encode_image(image_loaction):
    with open(image_loaction, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

client = Mistral(api_key=API_KEY)
path = str(input("Enter File Name: "))
image_path = f"{path}.jpeg"

base64image = encode_image(image_path)

ocr_response = client.ocr.process(
    model = "mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url" : f"data:image/jpeg;base64,{base64image}"
    }
)

print(ocr_response.pages[0].markdown)'''
from mistralai import Mistral
from thefuzz import fuzz, process

#API KEYS
try:
    API_KEY = "bZj0t7jIrakrUNvcmz9JaB0AZLdAWRND"
    client = Mistral(api_key=API_KEY)
except Exception:
    API_KEY = "B5rxs68cwfwWWE7zo53BXvAdawUOBQzE"
    client = Mistral(api_key=API_KEY)
except Exception:
    print("API Key not found. Please check your API Key.")

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


#To check Similarly between Answer Sheet and Answer Key
similarity = fuzz.token_sort_ratio(ocr_response_sheet, ocr_response_key)

print(f"\nSimilarity between Answer Sheet and Answer Key: {similarity}%")