from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import sys

load_dotenv()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")

base_dir=Path('PDF_to_NatLan/latex_with_context')
output_path=Path('data/split_by_subproblem/latex_with_context_embedding_3_large')

output_path.mkdir(parents=True, exist_ok=True)

def embed(text, client):

    response = client.embeddings.create(
        input = text,
        model = MODEL_NAME
    )

    return response.model_dump_json(indent=2)

# Process all .tex files in the base directory
def process_files(base_dir, output_path):
    counter = 0
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    print("🔄 Processing files...")
    print(client)
    print(MODEL_NAME)
    for tex_file in base_dir.glob("*.tex"):
        try:
            text = tex_file.read_text(encoding="utf-8")
            
            print(counter)

            # Generate embedding
            embedding = embed(text, client)

            # Write to output
            output_file = output_path / f"{tex_file.stem}.json"
            output_file.write_text(embedding, encoding="utf-8")

            print(f"Processed: {tex_file.name} -> {output_file.name}")
        except Exception as e:
            print(f"Error processing {tex_file.name}: {e}")
        
        counter += 1

    print("✅ All files processed.✅")
# Run the process
#if __name__ == "__main__":
    
process_files(base_dir, output_path)


"""is_debug = "pydevd" in sys.modules or hasattr(sys, "gettrace") and sys.gettrace() is not None
if is_debug:
    process_files(base_dir, output_path)
"""