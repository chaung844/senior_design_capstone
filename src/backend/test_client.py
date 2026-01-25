import os
import sys
import base64
import argparse
import mimetypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_source):
    """
    If image_source is a local file, convert to base64 data URI.
    If it's a URL (starts with http), return as is.

    Args:
        image_source (str): Local file path or URL of the image.

    Returns:
        str: Data URI string or original URL.
    """
    if image_source.startswith("http://") or image_source.startswith("https://"):
        return image_source
    
    if not os.path.exists(image_source):
        print(f"(!) Error: Local file not found: {image_source}")
        sys.exit(1)

    # Guess MIME type (e.g., image/jpeg, image/png)
    mime_type, _ = mimetypes.guess_type(image_source)
    if not mime_type:
        mime_type = "image/jpeg" # Default fallback

    with open(image_source, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Return formatted Data URI
    return f"data:{mime_type};base64,{base64_image}"

def main():
    parser = argparse.ArgumentParser(description="Test vLLM Inference Server on Modal")
    parser.add_argument("--url", type=str, default="https://t-anhtiep114--demo-vllm-inference-serve.modal.run", help="The full Modal URL")
    parser.add_argument("--key", type=str, help="Your VLLM_API_KEY")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-VL-8B-Instruct-FP8", help="The model name")
    parser.add_argument("--prompt", type=str, default="Introduce yourself.", help="The text prompt")
    parser.add_argument("--prompt-file", type=str, help="Path to a text file containing the prompt (overrides --prompt)")
    parser.add_argument("--image", type=str, help="URL OR Local Path of the image")
    
    args = parser.parse_args()

    base_url = args.url or os.getenv("MODAL_BASE_URL")
    
    # --- Base URL Validation ---
    if not base_url:
        print(" (!) Error: Missing URL.")
        sys.exit(1)

    if not base_url.endswith("/v1"):
        base_url = f"{base_url.rstrip('/')}/v1"

    print(f"(>) Connecting to: {base_url}")
    print(f"(>) Model: {args.model}")
    
    # --- Image Source ---
    if args.image:
        print(f"(>) Image Source: {args.image}")

    try:
        client = OpenAI(base_url=base_url, api_key="dummy")
    except Exception as e:
        print(f"(!) Failed to create client: {e}")
        sys.exit(1)

    # --- Load Prompt from File if Specified ---
    if args.prompt_file:
        if not os.path.exists(args.prompt_file):
            print(f"(!) Error: Prompt file not found: {args.prompt_file}")
            sys.exit(1)
        
        try:
            with open(args.prompt_file, "r", encoding="utf-8") as f:
                args.prompt = f.read().strip()
            print(f"(>) Loaded prompt from: {args.prompt_file}")
        except Exception as e:
            print(f"(!) Error reading prompt file: {e}")
            sys.exit(1)
    


    # --- Construct Message ---
    if args.image:
        # Convert local file to Base64 Data URI if necessary
        image_url = encode_image(args.image)

        user_content = [
            {"type": "text", "text": args.prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                },
            },
        ]
    else:
        user_content = args.prompt

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": user_content},
    ]

    print(f"User: {args.prompt}\n")
    print("Assistant: ", end="", flush=True)

    try:
        stream = client.chat.completions.create(
            model=args.model,
            messages=messages,
            stream=True,
            temperature=0.0,
            top_p=0.8,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            max_tokens=8096,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")

    except Exception as e:
        print(f"\n\n(!) API Request Failed: {e}")

if __name__ == "__main__":
    main()

    """
    uv run test_client.py \
    --image "safe/sample/receipt_11.jpg" \
    --prompt-file "prompts/receipts_parsing_instruction.md"
    """