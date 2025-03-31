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

#print(ocr_response.pages[0].markdown)

for page in ocr_response.pages:
    print(page.markdown)