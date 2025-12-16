import gradio as gr
from groq import Groq
import os
from dotenv import load_dotenv

# ---------- ENV ----------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

# ---------- CLIENT ----------
def get_client():
    return Groq(api_key=GROQ_API_KEY)

# ---------- SPEECH TO TEXT ----------
def transcribe_with_groq(audio_filepath):
    client = get_client()

    with open(audio_filepath, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3",
            language="en"
        )

    return transcription.text

# ---------- LLM EXTRACTION ----------
def generate_prescription(transcribed_text):
    prompt = f"""
You are a medical data extraction assistant.

Extract and return EXACTLY in this format:
Patient's Name:
Patient's Mobile Number:
Prescription:

Medical Dictation:
\"\"\"
{transcribed_text}
\"\"\"
"""

    client = get_client()
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_completion_tokens=1024
    )

    return completion.choices[0].message.content

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_prescription_pdf(prescription_text):
    file_name = f"prescription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Medical Prescription")

    c.setFont("Helvetica", 12)
    y = height - 100

    for line in prescription_text.split("\n"):
        c.drawString(50, y, line)
        y -= 18

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 50

    c.save()
    return file_name

def generate_prescription_and_pdf(transcribed_text):
    prescription = generate_prescription(transcribed_text)
    pdf_path = generate_prescription_pdf(prescription)
    return prescription, pdf_path

# ---------- UI ----------
with gr.Blocks(title="AI Prescription Generator") as demo:
    gr.Markdown("AI Voice Prescription Generator")
    
    audio_input = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="Record Your Voice"
    )

    submit_audio_btn = gr.Button("Submit Audio")

    stt_textbox = gr.Textbox(
        label="Speech to Text",
        lines=6
    )

    generate_btn = gr.Button("Generate Prescription")

    prescription_output = gr.Textbox(
        label="Generated Prescription",
        lines=8
    )

    pdf_output = gr.File(
        label="Download Prescription PDF"
    )

    # Step 1: Audio → Text
    submit_audio_btn.click(
        fn=transcribe_with_groq,
        inputs=audio_input,
        outputs=stt_textbox
    )

    # Step 2: Text → Prescription + PDF
    generate_btn.click(
        fn=generate_prescription_and_pdf,
        inputs=stt_textbox,
        outputs=[prescription_output, pdf_output]
    )

demo.launch(debug=True, share=True)
