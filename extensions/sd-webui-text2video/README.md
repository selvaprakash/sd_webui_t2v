# text2video Extension for AUTOMATIC1111's StableDiffusion WebUI

Auto1111 extension implementing various text2video models, such as ModelScope and VideoCrafter, using only Auto1111 webui dependencies and downloadable models (so no logins required anywhere)

## Requirements

### ModelScope

6 GBs vram should be enough to run on GPU with low vram vae on at 256x256 (and we are already getting reports of people launching 192x192 videos [with 4gbs of vram](https://github.com/deforum-art/sd-webui-modelscope-text2video/discussions/27)). 24 frames long 256x256 video definitely fits into 12gbs of NVIDIA GeForce RTX 2080 Ti, or if you have a Torch2 attention optimization supported videocard, you can fit the whopping 125 frames (8 seconds) long video into the same 12 GBs of VRAM! 250 frames (16 seconds) in the same conditions take 20 gbs.

Prompt: `best quality, anime girl dancing`

https://user-images.githubusercontent.com/14872007/232229730-82df36cc-ac8b-46b3-949d-0e1dfc10a975.mp4


We will appreciate *any* help with this extension, *especially* pull-requests.

### VideoCrafter (WIP, needs more devs to maintain properly as well)

VideoCrafter runs with around 9.2 GBs of VRAM with the settings set on Default.

## Major changes between versions

Update 2023-03-27: VAE settings and "Keep model in VRAM" moved to general webui setting under 'ModelScopeTxt2Vid' section. 

Update 2023-03-26: prompt weights **implemented**! (ModelScope only yet, as of 2023-04-05)

Update 2023-04-05: added VideoCrafter support, renamed the extension to plainly 'sd-webui-text2video'

Update 2023-04-13: in-framing/in-painting support: allows to 'animate' an existing pic or even seamlessly loop the videos! 

Update 2023-04-15: **MEGA-UPDATE**: Torch2/xformers optimizations, possible to make 125 frames long video on 12 gbs of VRAM. CPU offloading doesn't happen now if keep_pipe_in_vram is checked.

Update 2023-04-16: WebAPI is available!

## Test examples:

### ModelScope

Prompt: `cinematic explosion by greg rutkowski`

https://user-images.githubusercontent.com/14872007/226345611-a1f0601f-db32-41bd-b983-80d363eca4d5.mp4

Prompt: `really attractive anime girl skating, by makoto shinkai, cinematic lighting`

https://user-images.githubusercontent.com/14872007/226468406-ce43fa0c-35f2-4625-a892-9fb3411d96bb.mp4

**'Continuing' an existing image**

Prompt: `best quality, astronaut dog`

https://user-images.githubusercontent.com/14872007/232073361-bdb87a47-85ec-44d8-9dc4-40dab0bd0555.mp4

Prompt: `explosion`

https://user-images.githubusercontent.com/14872007/232073687-b7e78b06-182b-4ce6-b565-d6738c4890d1.mp4

**In-painting and looping back the videos**

Prompt: `nuclear explosion`

https://user-images.githubusercontent.com/14872007/232073842-84860a3e-fa82-43a6-a411-5cfc509b5355.mp4

Prompt: `best quality, lots of cheese`

https://user-images.githubusercontent.com/14872007/232073876-16895cae-0f26-41bc-a575-0c811219cf88.mp4

### VideoCrafter

Prompt: `anime 1girl reimu touhou`

https://user-images.githubusercontent.com/14872007/230231253-2fd9b7af-3f05-41c8-8c92-51042b269116.mp4

## Where to get the weights

### ModelScope

Download the following files from the [original HuggingFace repository](https://huggingface.co/damo-vilab/modelscope-damo-text-to-video-synthesis/tree/main). Alternatively, [download half-precision fp16 pruned weights (they are smaller and use less vram on loading)](https://huggingface.co/kabachuha/modelscope-damo-text2video-pruned-weights/tree/main):
- VQGAN_autoencoder.pth
- configuration.json
- open_clip_pytorch_model.bin
- text2video_pytorch_model.pth

And put them in `stable-diffusion-webui/models/ModelScope/t2v`. Create those 2 folders if they are missing. 

### VideoCrafter

Download pretrained T2V models either via [this link](https://drive.google.com/file/d/13ZZTXyAKM3x0tObRQOQWdtnrI2ARWYf_/view?usp=share_link) or download [the pruned half precision weights](https://huggingface.co/kabachuha/videocrafter-pruned-weights/tree/main), and put the `model.ckpt` in `models/VideoCrafter/model.ckpt`.

## Fine-tunes and how to use them

Thanks to https://github.com/ExponentialML/Text-To-Video-Finetuning you can fine-tune your models!

To utilize a fine-tuned model here, use [this script](https://github.com/ExponentialML/Text-To-Video-Finetuning/pull/52) which will convert the Diffusers-formatted model that repo outputs into the original weights format.

### Prominent Fine-tunes

**Potat1**

[Potat1](https://huggingface.co/camenduru/potat1) is a ModelScope-based model trained by @camenduru on 2197 clips with the resolution of 1024x576 which makes it the first open source hi-res text2video model. 

https://github.com/kabachuha/sd-webui-text2video/assets/14872007/ff01c6cb-0000-40a2-ac7e-ec3edc5f9713

To download the plug-and-play weights for the extension use this link https://huggingface.co/kabachuha/potat1-with-text-encoder-original-format.

**Animov-0.1**

[Animov-0.1 by strangeman3107](https://huggingface.co/datasets/strangeman3107/animov-0.1). The converted weights for this model reside [here](https://huggingface.co/kabachuha/animov-0.1-modelscope-original-format).

https://user-images.githubusercontent.com/14872007/232611542-600cec38-d944-4530-bc5c-3595a115c2be.mp4

## Screenshots

txt2vid with img2vid

![Screenshot 2023-04-15 at 17-53-36 Stable Diffusion](https://user-images.githubusercontent.com/14872007/232232319-c3a443ee-1a8a-4504-a114-d9da2ae916c2.png)

vid2vid

![Screenshot 2023-04-15 at 17-33-32 Stable Diffusion](https://user-images.githubusercontent.com/14872007/232232338-a2aa4b78-35d0-4c9b-850b-15edc90c0c9f.png)

## Dev resources

### ModelScope

HuggingFace space:

https://huggingface.co/spaces/damo-vilab/modelscope-text-to-video-synthesis

The model PyTorch implementation from ModelScope:

https://github.com/modelscope/modelscope/tree/master/modelscope/models/multi_modal/video_synthesis

Google Colab from the devs:

https://colab.research.google.com/drive/1uW1ZqswkQ9Z9bp5Nbo5z59cAn7I0hE6R?usp=sharing

### VideoCrafter

Github:

https://github.com/VideoCrafter/VideoCrafter
