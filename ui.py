import time
import requests
import gradio as gr

API_URL = "http://localhost:8000"

styles = [
    "photographic",
    "illustration",
    "animation",
    "cinematic",
    "sketch",
]
aspect_ratios = ["1:1", "16:9", "9:16"]
motions = [
    "pan_right",
    "pan_left",
    "tilt_down",
    "tilt_up",
    "zoom_in",
    "zoom_out",
    "rotate",
    "static",
]
voices = ["female_1", "female_2", "female_3", "male_1", "male_2", "male_3"]
music_styles = ["ambient", "upbeat", "dramatic", "peaceful"]


def run_generation(prompt, style, aspect_ratio, motion, voice, music_style,
                   preview):
    resp = requests.post(
        f"{API_URL}/generate",
        json={
            "prompt": prompt,
            "style": style,
            "aspect_ratio": aspect_ratio,
            "motion": motion,
            "voice": voice,
            "music_style": music_style,
            "preview": preview,
        },
        timeout=10,
    )
    task_id = resp.json()["task_id"]
    status = "queued"
    output_path = None
    while status not in {"done", "error"}:
        time.sleep(1)
        r = requests.get(f"{API_URL}/progress/{task_id}", timeout=10)
        data = r.json()
        status = data.get("status", "error")
        output_path = data.get("output_path")
    if status == "done" and output_path:
        return output_path
    raise gr.Error(data.get("error", "Generation failed"))


with gr.Blocks() as demo:
    gr.Markdown("# Prompt Video Generator")
    with gr.Row():
        prompt = gr.Textbox(label="Prompt")
    with gr.Row():
        style_dd = gr.Dropdown(
            styles, value="photographic", label="Style"
        )
        aspect_dd = gr.Dropdown(
            aspect_ratios, value="1:1", label="Aspect Ratio"
        )
        motion_dd = gr.Dropdown(motions, value="pan_right", label="Motion")
    with gr.Row():
        voice_dd = gr.Dropdown(voices, value="female_1", label="Voice")
        music_dd = gr.Dropdown(
            music_styles, value="ambient", label="Music Style"
        )
        preview_cb = gr.Checkbox(label="Preview", value=False)
    gen_btn = gr.Button("Generate")
    output = gr.Video(label="Result")
    gen_btn.click(
        run_generation,
        [
            prompt,
            style_dd,
            aspect_dd,
            motion_dd,
            voice_dd,
            music_dd,
            preview_cb,
        ],
        output,
    )

demo.queue()
demo.launch()
