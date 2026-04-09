import gradio as gr
from transformers import pipeline

print("Loading models... This may take a minute.")

asr = pipeline("automatic-speech-recognition", 
               model="openai/whisper-large-v3-turbo", 
               device="cpu")

translator = pipeline("translation", 
                      model="facebook/nllb-200-distilled-600M")

def translate(audio):
    if audio is None:
        return "No audio received. Speak into the microphone."
    
    text = asr({"sampling_rate": 16000, "raw": audio})
    translated = translator(text, src_lang="eng_Latn", tgt_lang="spa_Latn")[0]
    return translated

demo = gr.Interface(
    fn=translate,
    inputs=gr.Audio(source="microphone", type="numpy", label="Speak here"),
    outputs=gr.Textbox(label="Translation"),
    title="Universal Real-time Translator",
    description="Speak any language - Get instant translation (demo version)"
)

demo.launch()
