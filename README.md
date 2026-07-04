# comfyui-launcher-script
A simple script that diffuse-generate the name of ComfyUI at launch of a ComfyUI-portable installation

https://github.com/user-attachments/assets/eb666709-d660-44f2-8996-11fa0f96c924

## What's this ?
This is a simple Python script to be launched that emulates a diffusion animation with text characters and form the word "ComfyUI" (because... diffusion generative AI, right ?).

## Is it useless ?
Yes. But I thought this was nifty and fun instead of the normal boring .bat

## How does it work ?
#### Installation
Just place both files at the root of your ComfyUI-portable install, and run the .bat

```
C:\your\path\to\ComfyUI
  ├ advanced
  ├ python_embeded
  ├ ComfyUI
  ├ update
  ├── Comfylaunchconfig.json
  ├── launch_comfyui_anim.bat   <----- Run this one
  ├── launch_comfyui_anim.py
  └── run_nvidia_gpu.bat
```

The terminal window will pop up and play the animation, then wait for you to press a key to resume the launch of your ComfyUI instance with the parameters stored inside the __Comfylaunchconfig.json__.
At first launch, it will create the __Comfylaunchconfig.json__ with default values that correspond to the command line displayed under the green "ComfyUI" logo. If those aren't your typical arguments (which we all have our favorite mix of), then just close the terminal window and edit the .json to add your own and rerun the bat. You'll see your command line updated.

#### Advanced precision loading menu
Pressing "O" (the letter as in Oscar) when the ComfyUI logo is green will send you to a config menu with specific launch arguments to control the precision of the checkpoint, the encoders and the VAE, if you ever needed this. Just navigate with your keyboards arrows, and whichever settings are highlighted will be saved in the .json config file.

<img width="1222" height="514" alt="image" src="https://github.com/user-attachments/assets/031f26ff-31e1-4533-b1a5-102288500947" />

## Caveats (probably)
-> I've designed this to use with **ComfyUI portable** so the python environment location

-> I've only tested this on Windows where I operate, so there's no telling if the coded functions would work on Linux or other. Please let me know in the issues so others will know as well.

-> This is vibecoded as f*ck, so don't beat me up about the quality of the code, cheers
