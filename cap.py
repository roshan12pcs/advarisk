import requests

def extract_text_online(image_url):
    api_url = "https://api.ocr.space/parse/image"
    payload = {
        'url': image_url,
        'isOverlayRequired': False,
        'apikey': 'K81633010188957',  # demo key, use your own for production
        'language': 'eng'
    }

    try:
        response = requests.post(api_url, data=payload)
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            return f"OCR Error: {result.get('ErrorMessage', 'Unknown error')}"
        
        text = result["ParsedResults"][0]["ParsedText"]
        return text.strip() if text.strip() else "No text detected"

    except Exception as e:
        return f"Error during OCR API call: {e}"

# Test the function
image_url = "https://epanjiyan.rajasthan.gov.in/CImage.aspx?t=09/06/2025%2017:19:42"
print(extract_text_online(image_url))
