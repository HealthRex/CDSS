Learning Objective: 
How to (a) create a VM that is compatiple for running deep learning and LLM projects, (b) download and use LLaMA through python APIs. 

<h2 style="font-size:60px;">1. Creating VM</h2>
This tutorial assumes that you already have access to the HealthRex projects and have your VPN running. Following steps help you create a VM on our GCP:

<ul>
  <li>Navigate to our online GCP and on top left corner choose "som-nero-phi-jonc101-secure" project. Note, for processing clinical notes we should use this secure project as the notes may contain PHI.</li>
  <li>On far left, click on the "Navigation Menu" (the three horizontal bars icon), and choose "Google Engine" and then "VM Instances". This is the page that helps you define and create your VM. </li>
  <li>Click on the "CREATE INSTANCE" and you will be navigated to a page to define your system hardware and OS. Choose an approperiate name for your VM. You have the option to choose specific reageon and zone where your VM is or you can leave it as the default choices. Under "Machine Configuration" you can set up your VM hardware. Since we are going to use this VM for deep learning and LLM models, it is more effective to create a VM machine equiped with GPUs. Click on the "GPU" tab and choose the set up based on how large the model is. Please see the llama github page (https://github.com/facebookresearch/llama) for hardware requirement. For the smaller (7B model) llama model, 1 NVIDIA T4 GPU shoudl be enough. Next, you can define the number/amount of CPU and memory you need for your project.  </li>
</ul>
