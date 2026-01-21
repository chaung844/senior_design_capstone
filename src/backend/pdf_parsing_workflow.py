import os
import sys
from vllm import LLM, SamplingParams
from pdf2image import convert_from_path


# Model Configuration
# model_name = "Qwen/Qwen3-VL-8B-Instruct-FP8"  
model_name = "Qwen/Qwen3-VL-4B-Instruct"  
allowed_path = os.path.abspath("safe") # white list directory for file URLs 

# Prevent re-initialization in environments like Colab
if 'llm' in globals():
    print("(*) Model is already loaded! Skipping initialization to prevent crash.")
else:
    print("(*) Initializing vLLM... (This takes a minute)")
    try:
        llm = LLM(
            model=model_name,
            max_model_len=25096,
            limit_mm_per_prompt={"image": 4},
            tensor_parallel_size=1,
            allowed_local_media_path=allowed_path,
            dtype="bfloat16",
            # enforce_eager=True  # Enable for colab compatibility
        )
        print("(*) Model Loaded Successfully!")
    except Exception as e:
        print(f"(!) Initialization Failed: {e}")
        raise


# PDF parsing workflow ===================================================
pdf_path = "safe/sample/bankstatement_2.pdf"  
# pdf_path = "safe/sample/receipt_2.pdf"  
output_folder = "safe/output_images"

# Create output folder
os.makedirs(output_folder, exist_ok=True) 
print(f"(*) Parsing PDF:  {pdf_path}...")

try:
    # Convert PDF
    images = convert_from_path(pdf_path)
    
    # Save Images
    for i, image in enumerate(images):
        file_name = f"page_{i + 1}.jpg"
        save_path = os.path.join(output_folder, file_name)
        image.save(save_path, "JPEG")
        print(f"(*) Saved: {save_path}")

    print(f"(*) Finished converting PDF to images. Total pages: {len(images)}")

except Exception as e:
    print(f"(!) Error: {e}")


# data input
image_rel_path = "safe/output_images/page_1.jpg"
instruction_path = "prompts/bank_statement_parsing_instruction.md"
# instruction_path = "prompts/receipts_parsing_instruction.md"
default_user_query = "Extract all of the transactions from this bank statement."
image_urls = []

# iterate through a folder of images and process each
for image_file in os.listdir(output_folder):
    image_rel_path = os.path.join(output_folder, image_file)
    print(f"(*) Processing image file: {image_rel_path}")
    # Convert image path to URL
    if os.path.exists(image_rel_path):
        absolute_path = os.path.abspath(image_rel_path)
        image_url = f"file://{absolute_path}"
        print(f"(*) Processing image: {image_rel_path}")
    else:
        print(f"(!) Error: Image not found at {image_rel_path}")
        image_url = None
    image_urls.append(image_url)

# Load instruction from file (optional fallback to string)
if os.path.exists(instruction_path):
    with open(instruction_path, "r") as file:
        instruction_text = file.read()
else:
    instruction_text = default_user_query 

if image_urls:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_urls[0]}},
                {"type": "image_url", "image_url": {"url": image_urls[1]}},
                {"type": "image_url", "image_url": {"url": image_urls[2]}},
                {"type": "image_url", "image_url": {"url": image_urls[3]}},
                {"type": "text", "text": instruction_text},
            ],
        }
    ]

    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.8,
        repetition_penalty=1.05,
        max_tokens=8000,
    )

    print("Generating response...")
    outputs = llm.chat(messages=messages, sampling_params=sampling_params)

    for output in outputs:
        generated_text = output.outputs[0].text
        print(f"\n--- Output ---\n{generated_text}")
    print("(*) Response generation completed.")
    
    # save output to file
    output_text_path = "safe/generated_responses/parsed_bank_statement_transactions.yaml"
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)
    with open(output_text_path, "w") as out_file:
        out_file.write(generated_text)
    print(f"(*) Saved generated response to: {output_text_path}")
    