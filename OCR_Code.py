###
# !apt-get update && apt-get install -y tesseract-ocr
# !pip install pytesseract google-cloud-vision azure-ai-formrecognizer openai pillow pdf2image pandas flask-ngrok
# !apt-get install -y poppler-utils
#Install the required libraries,APIs
###
import os
import zipfile
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import pandas as pd
from google.colab import files

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

#create folders
if not os.path.exists("input_docs"):
    os.mkdir("input_docs")
if not os.path.exists("processed_images"):
    os.mkdir("processed_images")

#Upload multiple items
print("Please upload your documents (PDFs, images, ZIPs):")
uploaded_files = files.upload()

for file_name, content in uploaded_files.items():
    if file_name.endswith(".zip"):
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall("input_docs")
            print(f"Extracted ZIP file: {file_name}")
    elif file_name.endswith(".pdf"):
        pages = convert_from_path(file_name, dpi=300)
        for i, page in enumerate(pages):
            page.save(f"processed_images/{file_name}_page_{i+1}.jpg", "JPEG")
            print(f"Converted PDF page {i+1} of '{file_name}' to an image.")
    elif file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        with open(os.path.join("input_docs", file_name), "wb") as f:
            f.write(content)
            print(f"Uploaded image: {file_name}")
    else:
        print(f"Unsupported file type: {file_name}")

print("\nUploaded files in 'input_docs':", os.listdir("input_docs"))
print("\nProcessed images in 'processed_images':", os.listdir("processed_images"))

def handwritten_ocr(image_path):
    """Extract text from an image using Tesseract OCR."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def classify_document(text):
    """Classify the document based on keywords."""
    if "birth" in text.lower() and "certificate" in text.lower():
        return "Birth Certificate"
    elif "death" in text.lower() and "certificate" in text.lower():
        return "Death Certificate"
    elif "resume" in text.lower() or "cv" in text.lower():
        return "Resume"
    elif "vehicle" in text.lower() or "motor" in text.lower():
        return "Motor Vehicle Case Document"
    elif "license" in text.lower() and "driver" in text.lower():
        return "Driver's License"
    elif "aadhar" in text.lower() or "uidai" in text.lower():
        return "Aadhar Card"
    else:
        return "Unknown Document Type"

#Process All Uploaded Files ---
def process_documents(folder_path, processed_image_path):
    """Process and analyze files from input folders."""
    results = []

    # Process uploaded images
    for folder, subfolders, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(folder, filename)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"Processing image: {filename}")
                text = handwritten_ocr(file_path)
                doc_type = classify_document(text)
                results.append({"file": filename, "type": doc_type, "content": text})

    # Process converted images from PDFs
    for folder, subfolders, files in os.walk(processed_image_path):
        for filename in files:
            file_path = os.path.join(folder, filename)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"Processing converted image: {filename}")
                text = handwritten_ocr(file_path)
                doc_type = classify_document(text)
                results.append({"file": filename, "type": doc_type, "content": text})

    return results

def save_results_to_csv(results, output_file="ocr_results.csv"):
    """Save results to a CSV file."""
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to '{output_file}'.")

def display_results(results):
    """Display OCR results."""
    for result in results:
        print("\n---")
        print(f"File: {result['file']}")
        print(f"Type: {result['type']}")
        print(f"Content:\n{result['content']}")
        print("---")

def download_results(output_file="ocr_results.csv"):
    """Download the OCR results CSV file."""
    files.download(output_file)
    print(f"'{output_file}' is ready for download.")

print("\nStarting OCR processing...")
ocr_results = process_documents("input_docs", "processed_images")
save_results_to_csv(ocr_results)
display_results(ocr_results)

#Want to download Result
#download_results()
