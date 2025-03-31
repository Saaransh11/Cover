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

print(ocr_response.pages[0].markdown)