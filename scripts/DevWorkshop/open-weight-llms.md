# Running Open Weights Language Models on Remote GPUs


This tutorial guides you through setting up a virtual machine with GPUs on Google Cloud Services (GCS), accessing it from VS Code, and using it to run open-weight LLMs from Hugging Face with Keras-NLP and the JAX backend.

## Learning Goals

* Set up a virtual machine with GPUs on GCS.
* Access the VM from VS Code via SSH tunneling.
* Access open-weight LLMs from Hugging Face.
* Use these models for inference via Keras-NLP on the JAX backend.

## Prerequisites

* Google Stanford Account with VPN setup.
* Project `som-nero-phi-jonc101` permissions.
* A Hugging Face account (free).

## Setting up a GPU-enabled VM on GCS

1. Access the team's project on GCS: [https://console.cloud.google.com/compute/instances?project=som-nero-phi-jonc101](https://console.cloud.google.com/compute/instances?project=som-nero-phi-jonc101) (ensure you're connected with your `stanford.edu` account and the Stanford VPN is active).
2. Navigate to **Top Left Corner > Compute Engine > VM instances**.
3. If you encounter a "You need additional access to the project" message:
    * Request permission from Jonathan.
    * Email `srcc-support@stanford.edu` to request access for VM instantiation in the `som-nero-phi-jonc101` (and `som-nero-phi-jonc101-secure`) projects.
4. Click **CREATE INSTANCE**.
5. Configure the VM:
    * **Name:**  A descriptive name (e.g., `[your first name]-[GPU hardware]-[memory]` like `francois-l4-64gb`).
    * **Region and Zone:**  Choose a location (e.g., Region: `Oregon`, Zone: `us-west1-a`).
    * **Machine Configuration > GPUs:**
        * Start with 1 x NVIDIA L4.
        * **Machine type:** Select at least 64 GB of memory.
    * **Boot Disk:** Click "Switch Image", type "Pytorch" under Version, and select the latest PyTorch configuration (e.g., "Deep Learning VM for PyTorch 2.3 with CUDA 12.1 M125").
    * Click **Create**.
6. Once the VM is running (indicated by a checkmark), click **SSH** on the row's right hand side. This opens a terminal. Install the Nvidia driver when prompted (`y`).
7. 🚨 $\color{red}{\textbf{Important:}}$ Always stop your VM when finished (**Compute Engine > VM instances > Three vertical dots > Stop**) to avoid unnecessary charges. You can restart it later.

## Accessing your VM from VS Code via SSH Tunneling

1. Install the "Remote - SSH" extension in VS Code.
2. Open the SSH configuration file: **View > Command Palette > Remote-SSH: Open SSH Configuration File**. Choose the config file in your `.ssh` directory (e.g., `/Users/grolleau/.ssh/config`).
3. Add your VM configuration:
    * `Host`: A reference name (e.g., `remote-ssh-francois`).
    * `HostName`: Your VM's external IP from GCS (available in GCS in the row corresponding to your running VM instance).
    * `User`: Choose a username for use in the VM (e.g., `grolleau`).
4. Generate an SSH key:
    ```bash
    mkdir ~/mykeys
    cd ~/mykeys
    ssh-keygen -t rsa -f [reference name eg remote-ssh-francois] -C [username eg grolleau] -b 2048  # Leave passphrase empty
    ```
5. Add the key's path next to `IdentityFile` in your SSH config file:
    ```
    Host remote-ssh-francois
        HostName 34.169.68.90
        User grolleau
        IdentityFile /Users/grolleau/mykeys/remote-ssh-francois
    ```
6. Add the public key to your VM on GCS:
    * Copy the contents of `[reference name].pub` (e.g., `/Users/grolleau/mykeys/remote-ssh-francois.pub`).
    * In GCS, click on your VM, click "EDIT" at the top of the page, go to "SSH keys", click "Add item", paste the key in the empty cell. Click save at the bottom of the page.
7. Connect to the VM in VS Code: **Command Palette > Remote-SSH: Connect to Host > [reference name]**.

### Troubleshooting

* If your VM's external IP address changes (for example after restarting the VM), delete the contents of `~/.ssh/known_hosts` before connecting.

### Optional: Use a static external IP adress
This method prevents the external IP from changing when you restart your VM.
1. Reserve a static external IP adress
    * Navigate to **Top Left Corner > VPC Network > IP adresses**.
    * Make sure the drop down list on the top left indicates the same project where your VM is located (eg `som-nero-jonc101`).
    * Click **RESERVE EXTERNAL IP ADRESS**.
    * Provide a descriptive name (e.g., `francois-l4-64gb-static-external-ip`).
    * Select the same **Region** as your VM (e.g., `us-west1-a`).
    * Click **RESERVE**.
2. Assign the Static IP Address to Your VM
    * Navigate to **Top Left Corner > Compute Engine > VM instances**.
    * Click on your VM, then click **EDIT**.
    * In the **Network interfaces** section do **Network interface 1 > External IPv4 adress >** [*Name of your reserved static external IP adress*].
    * Click **SAVE**.

**Important:** Reserving a static external IP address incurs a small hourly charge (currently $0.005 per hour), which translates to approximately $44 per year. To avoid unnecessary costs, when you no longer need your VM, please delete it *AND* remember to do **Top Left Corner > VPC Network > IP adresses > RELEASE STATIC ADRESS**.
## Using Open Weights LLMs with Keras-NLP and JAX
1. Once VScode is SSH tunneled  to your VM, you'll have to reinstall all VScode extensions that you typically use. Thankfully that's easy: go to extensions in the SSH remote SSH tab click on the cloud icon and select the extensions you want to reinstall.
2. (Recommended) Create a conda environment.
3. Install the required packages (in this order):
```bash
    pip install --upgrade keras-nlp
    pip install --upgrade keras

    # Make sure to install the GPU version of JAX:
    pip install -U "jax[cuda12]" # This may throw an error; if the error is followed by "Successfully installed jax..." then this should be all good.
    
    pip install safetensors
    pip install --upgrade huggingface_hub
```
4. Select and setup the JAX backend
```python
import os
os.environ["KERAS_BACKEND"] = "jax"

# Allow the compiler to use 100% of the GPU memory
os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"]="1.00"

import keras_nlp
import keras

# Run at half precision to improve speed, sacrificing minimal performance
keras.config.set_dtype_policy("bfloat16")
```
5. Log in huggingface via Shell: `huggingface-cli login` and paste the token from huggingface.co on **Profile > Settings > Access Tokens > 3 vertical dots > Invalidate and refresh**. That token will be saved in `.cache/huggingface/token`, next time you can copy/paste from there.

### Gemma 2-2B Instruction Tuned
- Request access at https://huggingface.co/google/gemma-2b-it Authorization can take up to 24h.
```python
from keras_nlp.models import GemmaCausalLM

# Download the model
gemma_lm = keras_nlp.models.GemmaCausalLM.from_preset("hf://google/gemma-2-2b-it")

# Get a summary
gemma_lm.summary() # should see ~2B parameters and ~9.74 GB

# Ask a question
res = gemma_lm.generate("What is the nature of daylight?", max_length=64)
print(res)
```

### Llama-3-8B-Instruct
- Request access at https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct Authorization can take up to 24h.
```python
from keras_nlp.models import Llama3CausalLM

# Download the model
llama_lm = Llama3CausalLM.from_preset("hf://meta-llama/Meta-Llama-3-8B-Instruct")

# Get a summary
llama_lm.summary() # Should show 3B parameters ~29.92 GB

# Quantize the model to improve memory usage and speed, sacrificing minimal performance
llama_lm.quantize("int8")
llama_lm.summary() # Should show 3B parameters ~7.48 GB

# Prepare prompts in Llama3-appropriate format
def make_llama_3_prompt(user, system=""):
    system_prompt = ""
    if system != "":
        system_prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n\n{system}"
            f"<|eot_id|>"
        )
    prompt = (f"<|begin_of_text|>{system_prompt}"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{user}"
                f"<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )
    return prompt   

# Ask a simple question
prompt = make_llama_3_prompt(user="What is the meaning of life, the universe, and everything?", 
                             system="You are a superintelligent AI.")

res = llama_lm.generate(prompt, max_length=200)
print(res)
```

## Further reading
- LoRA / QLoRA fine-tuning of Gemma 2: [Tutorial 1](https://medium.com/@joansantoso/finetune-your-gemma-model-to-create-a-qa-model-f0380bfba710), [Tutorial 2](https://keras.io/examples/keras_recipes/parameter_efficient_finetuning_of_gemma_with_lora_and_qlora/)
- *Deep Learning with Python, Third Edition*: [pre-relase](https://www.manning.com/books/deep-learning-with-python-third-edition). This book is great! The latest chapters are currently being written and will include numerous code examples for how to use Keras 3 for LLM applications.

---

Tutorial created by François Grolleau on 10/10/2024.