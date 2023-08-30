Learning Objective: 
How to (a) create a VM that is compatiple for running deep learning and LLM projects, (b) download and use LLaMA through python APIs. 

<h2 style="font-size:60px;">1. Creating VM</h2>
This tutorial assumes that you already have access to the HealthRex projects and have your VPN running. Following steps help you create a VM on our GCP:

<ul>
  <li>Navigate to our online GCP and on top left corner choose "som-nero-phi-jonc101-secure" project. Note, for processing clinical notes we should use this secure project as the notes may contain PHI.</li>
  <li>On far left, click on the "Navigation Menu" (the three horizontal bars icon), and choose "Google Engine" and then "VM Instances". This is the page that helps you define and create your VM. </li>
  <li>Click on the "CREATE INSTANCE" and you will be navigated to a page to define your system hardware and OS. Choose an approperiate name for your VM. You have the option to choose specific reageon and zone where your VM is or you can leave it as the default choices. Under "Machine Configuration" you can set up your VM hardware. Since we are going to use this VM for deep learning and LLM models, it is more effective to create a VM machine equiped with GPUs. Click on the "GPU" tab and choose the set up based on how large the model is. Please see the llama github page (https://github.com/facebookresearch/llama) for hardware requirement. For the smaller (7B model) llama model, 1 NVIDIA T4 GPU shoudl be enough. Next, you can define the number/amount of CPU and memory you need for your project. There are other settings that you can modify/adjust, but the next important setting is "Boot Disk". GCP should now show you a warning "The selected image requires you to install an NVIDIA CUDA stack manually. To skip manual setup, click "Switch Image" below to use a GPU-optimized Debian OS image with CUDA support at no additional cost." It'd be easier to use one of the default system images of GCP, otherwise you'd need to install everything including cuda yourself. Click on the SWITCH IMAGE and under the "version" drop box you can choose the deep learning libraries your projects require (at the time of this tutorial I chose: Deep Learning VM for PyTorch 2.0 with CUDA 11.8 M110). Also, you can choose the amount of disk you need. Once, you are done defining the version and size you can click "Select" and you'll be back in the VM setting page. Select create and your VM will be created  </li>
</ul>

After creating your VM, you should see your VM under the "VM instances" list/window. Your VM is by defult on and running (you can probably see that the status small button is green). IMPORTANT NOTE, YOU SHOULD TURN OFF THE VM WHEN YOU ARE NOT USING IT AS GCP CHARGES BASED ON THE TIMES YOUR VM IS RUNNING. To stop the VM from running, you need to click on the "More Action" (the three small dots on the right) and click stop. Note, your settings and files will not be deleting by stoping the VM, but your running programs will stop. The next step is to access your VM through SSH and you can simply do that by clicking on the "SSH" bottun. A new command line tab will be open where you can use linux commands to work with your VM. Note, the first time you ssh to your VM it will ask your permission to install the required packages, enter y and press enter to give the permission. 

<h2 style="font-size:60px;">2. Downloading and using LLaMA </h2>

The first step is to fill out the request from from Meta here: https://ai.meta.com/llama/ and within 48 hours you will receive an email from Meta including a url and some information about the models (typically takes under an hour in most cases though). You will need this url in later steps. Following steps help you download the llama model on the VM you created above: 

<ul>
  <li>Run your VM and click on the ssh button to open a command line tabe (if you already don't have this open)</li>
  <li>The github page for the llama model is here: https://github.com/facebookresearch/llama. You should see a "download.sh" file on their github. You need to donwload that file on on your VM and then running that file will download the llama. You can just download it and then upload it to your VM via the UI (you can upload files to your VM via the "UPLOAD FILE" button on top right corner of your ssh). Alternatively, you can run this command in your ssh command line to download the file:

    `wget https://raw.githubusercontent.com/facebookresearch/llama/main/download.sh`</li>
</ul>





