import subprocess

import modal
from dotenv import load_dotenv
from openai import AsyncOpenAI

# --- config ---
MODEL_NAME = "Qwen/Qwen3-VL-8B-Instruct-FP8"
MODEL_REVISION = "9cdc6310a8cb770ce18efaf4e9935334512aee45"
VLLM_PORT = 8000
FAST_BOOT = True
MAX_MODEL_LEN = 26096
N_GPU = 1
MINUTES = 60  # seconds
VLLM_PORT = 8000

load_dotenv()  # Load environment variables from .env file

# --- Image Definition ---
# Using NVIDIA's CUDA image as a base and install vLLM using uv
vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install(  # <--- Using uv for fast remote installation
        "vllm==0.13.0",
        "huggingface-hub==0.36.0",
    )
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})  # Faster model transfers
)

# --- Volume Setup ---
# Create specific volumes for model weights and vLLM cache to persist data
hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

app = modal.App("demo-vllm-inference")

# api_key_secret = modal.Secret.from_name("vllm-secret")


@app.function(
    image=vllm_image,
    gpu=f"L4:{N_GPU}",
    scaledown_window=15 * MINUTES,  # how long should we stay up with no requests?
    timeout=10 * MINUTES,  # how long should we wait for container start?
    # secrets=[api_key_secret],
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
)
@modal.concurrent(  # how many requests can one replica handle? tune carefully!
    max_inputs=32
)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    # VLLM_API_KEY = os.environ.get("VLLM_API_KEY")

    # if not VLLM_API_KEY:
    #     print("WARNING: VLLM_API_KEY not found in environment. Defaulting to empty string.")
    #     VLLM_API_KEY = "" # Avoid NoneType error in join()

    cmd = [
        "vllm",
        "serve",
        "--uvicorn-log-level=info",
        MODEL_NAME,
        "--revision",
        MODEL_REVISION,
        "--served-model-name",
        MODEL_NAME,
        "llm",
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--max-model-len",
        str(MAX_MODEL_LEN),
        "--gpu-memory-utilization",
        "0.95",
        # "--api-key", VLLM_API_KEY,
    ]

    # enforce-eager disables both Torch compilation and CUDA graph capture
    # default is no-enforce-eager. see the --compilation-config flag for tighter control
    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]

    # assume multiple GPUs are for splitting up large matrix multiplications
    cmd += ["--tensor-parallel-size", str(N_GPU)]

    print(*cmd)

    subprocess.Popen(" ".join(cmd), shell=True)


@app.local_entrypoint()
async def test(test_timeout=600, content=None, twice=True):
    url = serve.get_web_url()
    print(f"    (*) Connect to: {url}")

    # # get api key from environment variable
    # load_dotenv()
    # api_key = os.environ.get("VLLM_API_KEY", "")
    # print(f"    (*) Using API Key: {'*' * len(api_key)}")

    # 1. Setup the OpenAI Client pointing to your Modal URL
    client = AsyncOpenAI(base_url=f"{url}/v1", api_key="dummy")

    # 2. Define prompts
    system_prompt = {
        "role": "system",
        "content": "You are a pirate who can't help but drop sly reminders that he went to Harvard.",
    }
    if content is None:
        content = "Explain the singular value decomposition."

    messages = [
        system_prompt,
        {"role": "user", "content": content},
    ]

    # 3. Helper function to stream response (replaces _send_request)
    async def run_query(msgs):
        print(f"\n  (>) Sending query: {msgs[-1]['content']}")
        try:
            stream = await client.chat.completions.create(
                model=MODEL_NAME,  # This must match what you passed to vllm serve
                messages=msgs,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()  # Newline after stream
        except Exception as e:
            print(f"    (!) Error: {e}")

    # 4. Execute Tests
    await run_query(messages)

    if twice:
        messages[0]["content"] = "You are Jar Jar Binks."
        await run_query(messages)
