# Copyright (C) 2023 by Artem Khrapov (kabachuha)
# Read LICENSE for usage terms.

import gradio as gr
from types import SimpleNamespace
from t2v_helpers.video_audio_utils import find_ffmpeg_binary
import os
from modules.shared import opts

welcome_text_videocrafter = '''
    Download pretrained T2V models via this link https://drive.google.com/file/d/13ZZTXyAKM3x0tObRQOQWdtnrI2ARWYf_/view?usp=share_link, and put the model.ckpt in models/VideoCrafter/model.ckpt.
    Then use the same GUI pipeline as ModelScope does.
'''

welcome_text_modelscope = '''Put your models from <a style="color:SteelBlue" href="https://huggingface.co/damo-vilab/modelscope-damo-text-to-video-synthesis/tree/main">https://huggingface.co/damo-vilab/modelscope-damo-text-to-video-synthesis/tree/main</a> to stable-diffusion-webui/models/ModelScope/t2v/. Make sure, you downloaded the file named 'configuration.json' in its raw text form (click on the ⬇️ character to the right, don't save via right-click).

8gbs of VRAM on top of SD should be enough to launch (when the VAE unloading will be fixed, before that orient around ~12 gbs).

Join the development or report issues and feature requests here <a style="color:SteelBlue" href="https://github.com/deforum-art/sd-webui-modelscope-text2video">https://github.com/deforum-art/sd-webui-modelscope-text2video</a>

<italic>If you liked this extension, please <a style="color:SteelBlue" href="https://github.com/deforum-art/sd-webui-modelscope-text2video">give it a star on GitHub</a>!</italic> 😊

'''

welcome_text = '''VideoCrafter (WIP):

''' + welcome_text_videocrafter + '''

ModelScope:

''' + welcome_text_modelscope

i1_store_t2v = f"<p style=\"text-align:center;font-weight:bold;margin-bottom:0em\">text2video extension for auto1111 — version 1.2b. The video will be shown below this label when ready</p>"

def setup_common_values(mode, d):
    with gr.Row(elem_id=f'{mode}_prompt_toprow'):
        prompt = gr.Textbox(label='Prompt', lines=3, interactive=True, elem_id=f"{mode}_prompt", placeholder="Enter your prompt here...")
    with gr.Row(elem_id=f'{mode}_n_prompt_toprow'):
        n_prompt = gr.Textbox(label='Negative prompt', lines=2, interactive=True, elem_id=f"{mode}_n_prompt", value=d.n_prompt)
    with gr.Row():
        steps = gr.Slider(label='Steps', minimum=1, maximum=100, step=1, value=d.steps)
        cfg_scale = gr.Slider(label='CFG scale', minimum=1, maximum=100, step=1, value=d.cfg_scale)
    with gr.Row():
        width = gr.Slider(label='Width', minimum=64, maximum=1024, step=64, value=d.width)
        height = gr.Slider(label='Height', minimum=64, maximum=1024, step=64, value=d.height)
    with gr.Row():
        seed = gr.Number(label='Seed', value = d.seed, Interactive = True, precision=0)
        eta = gr.Number(label="ETA", value=d.eta, interactive=True)
    with gr.Row():
        gr.Markdown('256x256 Benchmarks: 24 frames peak at 5.7 GBs of VRAM and 125 frames peak at 11.5 GBs with Torch2 installed')
    with gr.Row():
        frames = gr.Slider(label="Frames", value=d.frames, minimum=2, maximum=250, step=1, interactive=True, precision=0)
        batch_count = gr.Slider(label="Batch count", value=d.batch_count, minimum=1, maximum=100, step=1, interactive=True)
    
    return prompt, n_prompt, steps, seed, cfg_scale, width, height, eta, frames, batch_count

def setup_text2video_settings_dictionary():
    d = SimpleNamespace(**T2VArgs())
    dv = SimpleNamespace(**T2VOutputArgs())
    with gr.Row(elem_id='model-switcher'):
        model_type = gr.Radio(label='Model type', choices=['ModelScope', 'VideoCrafter (WIP)'], value='ModelScope', elem_id='model-type')
    with gr.Tabs():
        do_vid2vid = gr.State(value=0)
        with gr.Tab('txt2vid') as tab_txt2vid:
            # TODO: make it how it's done in Deforum/WebUI, so we won't have to track individual vars
            prompt, n_prompt, steps, seed, cfg_scale, width, height, eta, frames, batch_count = setup_common_values('txt2vid', d)
            with gr.Accordion('img2vid', open=False):
                inpainting_image = gr.File(label="Inpainting image", interactive=True, file_count="single", file_types=["image"], elem_id="inpainting_chosen_file")
                # TODO: should be tied to the total frame count dynamically
                inpainting_frames=gr.Slider(label='inpainting frames',value=d.inpainting_frames,minimum=0, maximum=24, step=1)
                with gr.Row():
                    gr.Markdown('''`inpainting frames` is the number of frames inpainting is applied to (counting from the beginning)

The following parameters are exposed in this keyframe: max frames as `max_f`, inpainting frames as `max_i_f`, current frame number as `t`, seed as `s`

The weigths of `0:(t/max_i_f), "max_i_f":(1)` will *continue* the initial pic

To *loop it back*, set the weight to 0 for the first and for the last frame

Example: `0:(0), "max_i_f/4":(1), "3*max_i_f/4":(1), "max_i_f-1":(0)` ''')
                with gr.Row():
                    inpainting_weights = gr.Textbox(label="Inpainting weights", value=d.inpainting_weights, interactive=True)
                
                def update_max_inp_frames(f, i_frames): # Show video
                    return gr.update(value=min(f, i_frames), maximum=f, visible=True)
                
                frames.change(fn=update_max_inp_frames, inputs=[frames, inpainting_frames], outputs=[inpainting_frames])
        with gr.Tab('vid2vid') as tab_vid2vid:
            with gr.Row():
                gr.HTML('Put your video here')
                gr.HTML('<strong>Vid2vid for VideoCrafter is to be done!</strong>')
            vid2vid_frames = gr.File(label="Input video", interactive=True, file_count="single", file_types=["video"], elem_id="vid_to_vid_chosen_file")
            with gr.Row():
                gr.HTML('Alternative: enter the relative (to the webui) path to the file')
            with gr.Row():
                vid2vid_frames_path = gr.Textbox(label="Input video path", interactive=True, elem_id="vid_to_vid_chosen_path", placeholder='Enter your video path here, or upload in the box above ^')
            # TODO: here too
            prompt_v, n_prompt_v, steps_v, seed_v, cfg_scale_v, width_v, height_v, eta_v, frames_v, batch_count_v = setup_common_values('vid2vid', d)
            with gr.Row():
                strength = gr.Slider(label="denoising strength", value=d.strength, minimum=0, maximum=1, step=0.05, interactive=True)
                vid2vid_startFrame=gr.Slider(label='vid2vid start frame',value=d.vid2vid_startFrame, minimum=0, maximum=23)
            
            def update_max_vid_frames(v2v_frames, sFrame): # Show video
                return gr.update(value=min(sFrame, v2v_frames-1), maximum=v2v_frames-1, visible=True)
            
            frames_v.change(fn=update_max_vid_frames, inputs=[frames_v, vid2vid_startFrame], outputs=[vid2vid_startFrame])
        
        tab_txt2vid.select(fn=lambda: 0, inputs=[], outputs=[do_vid2vid])
        tab_vid2vid.select(fn=lambda: 1, inputs=[], outputs=[do_vid2vid])

        with gr.Tab('Output settings'):
            with gr.Row(variant='compact') as fps_out_format_row:
                fps = gr.Slider(label="FPS", value=dv.fps, minimum=1, maximum=240, step=1)
            with gr.Row(variant='compact') as soundtrack_row:
                add_soundtrack = gr.Radio(['None', 'File', 'Init Video'], label="Add soundtrack", value=dv.add_soundtrack)
                soundtrack_path = gr.Textbox(label="Soundtrack path", lines=1, interactive=True, value=dv.soundtrack_path)

            with gr.Row(variant='compact'):
                skip_video_creation = gr.Checkbox(label="Skip video creation", value=dv.skip_video_creation, interactive=True)
            with gr.Row(equal_height=True, variant='compact', visible=True) as ffmpeg_set_row:
                ffmpeg_crf = gr.Slider(minimum=0, maximum=51, step=1, label="CRF", value=dv.ffmpeg_crf, interactive=True)
                ffmpeg_preset = gr.Dropdown(label="Preset", choices=['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster', 'veryfast', 'superfast', 'ultrafast'], interactive=True, value=dv.ffmpeg_preset, type="value")
            with gr.Row(equal_height=True, variant='compact', visible=True) as ffmpeg_location_row:
                ffmpeg_location = gr.Textbox(label="Location", lines=1, interactive=True, value=dv.ffmpeg_location)
        with gr.Tab('How to install? Where to get help, how to help?'):
            gr.Markdown(welcome_text)

    return locals()

t2v_video_args_names = str('skip_video_creation, ffmpeg_location, ffmpeg_crf, ffmpeg_preset, fps, add_soundtrack, soundtrack_path').replace("\n", "").replace("\r", "").replace(" ", "").split(',')

common_values_names = str('''prompt, n_prompt, steps, frames, seed, cfg_scale, width, height, eta, batch_count''').replace("\n", "").replace("\r", "").replace(" ", "").split(',')

v2v_values_names = str('''
do_vid2vid, vid2vid_frames, vid2vid_frames_path, strength,vid2vid_startFrame,
inpainting_image,inpainting_frames, inpainting_weights,
model_type''').replace("\n", "").replace("\r", "").replace(" ", "").split(',')

t2v_args_names = common_values_names + [f'{v}_v' for v in common_values_names] + v2v_values_names

t2v_args_names_cleaned = common_values_names + v2v_values_names

def get_component_names():
    return t2v_video_args_names + t2v_args_names

def pack_anim_args(args_dict):
    return {name: args_dict[name] for name in t2v_args_names_cleaned}

def pack_video_args(args_dict):
    return {name: args_dict[name] for name in t2v_video_args_names}

def process_args(args_dict):
    if args_dict['do_vid2vid']:
        # override text2vid data with vid2vid data
        for name in common_values_names:
            args_dict[name] = args_dict[f'{name}_v']
    
    # deduplicate
    for name in common_values_names:
        if f'{name}_v' in args_dict:
            args_dict.pop(f'{name}_v')

    args = SimpleNamespace(**pack_anim_args(args_dict))
    video_args = SimpleNamespace(**pack_video_args(args_dict))
    T2VArgs_sanity_check(args)
    return args, video_args

def T2VArgs():
    frames = 24
    batch_count = 1
    eta = 0
    seed = -1
    width = 256
    height = 256
    cfg_scale = 17
    steps = 30
    prompt = ""
    n_prompt = "text, watermark, copyright, blurry, nsfw"
    strength = 0.75
    vid2vid_startFrame = 0
    inpainting_weights = '0:(t/max_i_f), "max_i_f":(1)' # linear growth weights (as they used to be in the original variant)
    inpainting_frames = 0
    return locals()

def T2VArgs_sanity_check(t2v_args):
    try:
        if t2v_args.frames < 1:
            raise ValueError('Frames count cannot be lower than 1!')
        if t2v_args.batch_count < 1:
            raise ValueError('Batch count cannot be lower than 1!')
        if t2v_args.width < 1 or t2v_args.height < 1:
            raise ValueError('Video dimensions cannot be lower than 1 pixel!')
        if t2v_args.cfg_scale < 1:
            raise ValueError('CFG scale cannot be lower than 1!')
        if t2v_args.steps < 1:
            raise ValueError('Steps cannot be lower than 1!')
        if t2v_args.strength < 0 or t2v_args.strength > 1:
            raise ValueError('vid2vid strength should be in range of 0 to 1!')
        if t2v_args.vid2vid_startFrame >= t2v_args.frames:
            raise ValueError('vid2vid start frame cannot be greater than the number of frames!')
        if t2v_args.inpainting_frames < 0 or t2v_args.inpainting_frames > t2v_args.frames:
            raise ValueError('inpainting frames count should lie between 0 and the frames number!')
    except Exception as e:
        print(t2v_args)
        raise e

def T2VOutputArgs():
    skip_video_creation = False
    fps = 15
    make_gif = False
    delete_imgs = False  # True will delete all imgs after a successful mp4 creation
    image_path = "C:/SD/20230124234916_%09d.png"
    mp4_path = "testvidmanualsettings.mp4"
    ffmpeg_location = find_ffmpeg_binary()
    ffmpeg_crf = '17'
    ffmpeg_preset = 'slow'
    add_soundtrack = 'None'  # ["File","Init Video"]
    soundtrack_path = "https://deforum.github.io/a1/A1.mp3"
    # End-Run upscaling
    r_upscale_video = False
    r_upscale_factor = 'x2'  # ['2x', 'x3', 'x4']
    # 'realesr-animevideov3' (default of realesrgan engine, does 2-4x), the rest do only 4x: 'realesrgan-x4plus', 'realesrgan-x4plus-anime'
    r_upscale_model = 'realesr-animevideov3'
    r_upscale_keep_imgs = True

    render_steps = False
    path_name_modifier = "x0_pred"  # ["x0_pred","x"]
    # **Interpolate Video Settings**
    frame_interpolation_engine = "None"  # ["None", "RIFE v4.6", "FILM"]
    frame_interpolation_x_amount = 2  # [2 to 1000 depends on the engine]
    frame_interpolation_slow_mo_enabled = False
    frame_interpolation_slow_mo_amount = 2  # [2 to 10]
    frame_interpolation_keep_imgs = False
    return locals()

def get_outdir():
    outdir = os.path.join(opts.outdir_img2img_samples, 'text2video')
    outdir = os.path.join(os.getcwd(), outdir)
    return outdir