# vLLM running guide

## Running on Google Colab



## Running locally

### on Window
> vLLM need to run on Window Subsystem Linux (WSL)
- Install WSL
    ```shell
    wsl --install
    ```
    - Restart computer then enter username and password for wsl (this is separate from window login)
- Install **C compiler** (gcc and g++) on WSL
    ```shell
    sudo apt install -y build-essential
    ```
    - Make sure C compiler is installed
    ```shell
    gcc --version
    g++ --version
    ```
- Install NVIDIA Cuda Compiler (NVCC)
    ```shell
    sudo apt update
    sudo apt install -y nvidia-cuda-toolkit
    ```
    - Make sure NVCC is installed 
    ```shell
    nvcc --version
    ```


### on Linux

### on MacOS - unsupported


## Debugging
- View downloaded/cached model from HF
```shell
ls -lh ~/.cache/huggingface/hub/
``` 
- Fail to create `.venv` folder with `uv`
```shell
sudo chown -R [username]:[username] ~/[proj_folder]
```