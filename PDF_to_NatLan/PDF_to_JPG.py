import os
from pdf2image import convert_from_path

# Define paths
pdf_folder = "PDF_to_NatLan/PDFs"
jpg_folder = "PDF_to_NatLan/JPGs"

# Make sure the output folder exists
os.makedirs(jpg_folder, exist_ok=True)

# Process each matching PDF
for filename in os.listdir(pdf_folder):
    if filename.endswith("_Redacted.pdf"):
        student_id = filename.split("_")[0]  # Extract 'ddd' (student ID)
        pdf_path = os.path.join(pdf_folder, filename)
        
        # Convert PDF pages to images
        pages = convert_from_path(pdf_path, 500)
        
        for count, page in enumerate(pages):
            output_filename = f"{student_id}_{count}.jpg"
            output_path = os.path.join(jpg_folder, output_filename)
            page.save(output_path, 'JPEG')
            print(f"Saved: {output_path}")

print("All PDFs converted to JPGs.")