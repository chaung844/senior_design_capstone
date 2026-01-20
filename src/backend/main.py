import os
from vllm import LLM, SamplingParams

# --- CONFIGURATION ---
model_name = "Qwen/Qwen3-VL-8B-Instruct-FP8" 
image_rel_path = "sample/receipt_6.jpg"
instruction_path = "prompts/receipts_parsing_instruction.md"

# whitelist directory for file URLs
allowed_path = os.path.abspath("sample")

# setup
llm = LLM(
    model=model_name,
    max_model_len=4096, 
    limit_mm_per_prompt={"image": 1},
    tensor_parallel_size=1,
    # gpu_memory_utilization=0.8,
    allowed_local_media_path=allowed_path,
)

# sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.8,
    repetition_penalty=1.05,
    max_tokens=512,
)

# get input data

# check and convert image path to file URL
if os.path.exists(image_rel_path):
    absolute_path = os.path.abspath(image_rel_path)
    image_url = f"file://{absolute_path}"
else:
    raise FileNotFoundError(f"Could not find image at {image_rel_path}")

# load instruction text
instruction_text = "Extract the total amount and date from this receipt." 
if os.path.exists(instruction_path):
    with open(instruction_path, "r") as file:
        instruction_text = file.read()

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": instruction_text},
        ],
    }
]

# run inference
print("Generating...")
outputs = llm.chat(messages=messages, sampling_params=sampling_params)

# print results
for output in outputs:
    generated_text = output.outputs[0].text
    print(f"\n--- Output ---\n{generated_text}")