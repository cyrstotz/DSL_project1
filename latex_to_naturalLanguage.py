"""
Script: to-latex-folder.py
Author: Daria

This script processes a folder of scanned student solution images (JPEG format),
transcribes all visible handwritten and printed content into LaTeX using Azure OpenAI's Vision capabilities,
and saves the result as a `.tex` file for each image.

Features:
- Encodes images in base64 for API processing
- Sends each image to Azure OpenAI for transcription
- Implements retry logic for robustness
- Preserves logical structure and ignores content marked as deleted
- Includes footer metadata in output (e.g., student ID, page number)
- Saves results in a dedicated output folder

Requirements:
- Azure OpenAI access and credentials stored in a `.env` file
- Required packages: openai, python-dotenv

Usage:
- Set `FOLDER_PATH` to the directory containing your `.jpg` images
- Run the script: `python to-latex-folder.py`

Output:
- A subfolder named `<input_folder>_latex` will be created
- Each `.jpg` file will produce a corresponding `.tex` file
"""
# === to-latex-folder.py ===

from pathlib import Path
import base64
import time
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import pandas as pd

# === Load environment variables from .env ===
load_dotenv()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")
print(f"Model name: {MODEL_NAME}")
# === Functions ===


def process_function(content, filename, client, max_retries=3):
    """
    Process a single image using Azure OpenAI API with retry logic.
    """
    attempt = 0
    
    while attempt < max_retries:
        attempt += 1
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME, 
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "The attached text is a subtask from a student solution. Your goal is to translate the latex content into natural language. If no content is found, return 'No content found' but if anything is in the file translate it. If you find German words, translate them to English. Ignore titles as item a) or similar. "
                        )
                    },
                    {
                        "role": "user", 
                        "content": [
                            { 
                                "type": "text",
                                "text": f"translate the following latex text to natural language, use words to describe the latex content, as example: 'x^2 + 2x + 1 = 0' -> 'The equation x squared plus two x plus one equals zero.'. Don't leave anything out that can possibly be a part of the solution :\n\n {content}"
                            },
                        ]
                    }
                ],
                temperature=0.1
            )
            # If successful, return the content.
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error processing {filename} (attempt {attempt}/{max_retries}): {str(e)}")
            
            # If we haven't reached max_retries, wait a bit then retry.
            if attempt < max_retries:
                print("Retrying...")
                time.sleep(5)  # Wait 5 seconds before retrying
                
    # If all retries fail, return error text.
    return f"Error: failed to process {filename} after {max_retries} attempts."

def save_result(text, output_path):
    """
    Save the response text to a file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    print(f"Result saved to: {output_path}")

def process_folder(input_folder):
    """
    Process all images in a given folder and save results in a new folder.
    Keeps the image name for ordering, and adds a delay between requests.
    Retries if something fails.
    """
    input_folder = Path(input_folder)
    output_folder = input_folder.parent / f"natural_language"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    
    data = []
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".tex"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                # Optionally process the content
                if process_function:
                    content = process_function(content,filename, client,max_retries=3)
                data.append({"filename": filename, "content": content})
        
        # Save the result using the same stem + .txt
        filename = filename.replace(".tex", ".txt")
        output_file = output_folder / f"{filename}"
        save_result(content, output_file)
        
        # Delay to avoid rate limits (adjust as needed)
        #time.sleep(2)

    print(f"✅ All files processed ✅ Results saved in {output_folder}")

# === Main ===
if __name__ == "__main__":
    FOLDER_PATH = "data/split_by_subproblem/latex"  # Change this to your folder name
    process_folder(FOLDER_PATH)
