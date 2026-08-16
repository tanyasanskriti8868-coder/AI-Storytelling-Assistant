from datetime import datetime
from io import BytesIO
import random

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from config import Config
from qwen_engine import QwenEngine
from tts_engine import TTSEngine


st.set_page_config(
    page_title="Arcanova AI",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --bg: #1b1036;
    --bg-soft: #27144d;
    --panel: #ffffff;
    --edge: #3f2383;
    --primary: #6c35ff;
    --accent: #8d66ff;
    --text-dark: #1b1036;
    --text-light: #f8f6ff;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(900px 450px at 15% 0%, #3a1f7a 0%, transparent 60%),
        radial-gradient(800px 420px at 90% 100%, #2a1658 0%, transparent 60%),
        linear-gradient(135deg, var(--bg) 0%, #130a29 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #221245 0%, #1a0f36 100%);
    border-right: 1px solid #4b2b9c;
}

h1, h2, h3, label, span, p {
    color: var(--text-light) !important;
}

.panel {
    background: var(--panel);
    border: 1px solid #d9d2ef;
    border-radius: 16px;
    padding: 18px;
    color: var(--text-dark);
    box-shadow: 0 10px 30px rgba(19, 10, 41, 0.32);
}

.story-box {
    background: #ffffff;
    color: var(--text-dark);
    border: 1px solid #ddd6f3;
    border-radius: 14px;
    padding: 18px;
    line-height: 1.75;
    animation: reveal 0.45s ease-out;
}

.tag-chip {
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 8px;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid #5f3eb6;
    color: #f8f6ff;
    background: rgba(141, 102, 255, 0.14);
    font-size: 0.85rem;
}

.stButton > button {
    border: 0;
    border-radius: 12px;
    color: #ffffff;
    font-weight: 700;
    background: linear-gradient(120deg, var(--primary), var(--accent));
    box-shadow: 0 8px 24px rgba(108, 53, 255, 0.38);
    transition: transform 0.2s ease, filter 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.06);
}

div[data-baseweb="select"] > div,
textarea,
input {
    background: #ffffff !important;
    color: #140b29 !important;
}

@keyframes reveal {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""",
    unsafe_allow_html=True,
)


def get_mode_instructions() -> dict:
    return {
        "Character Tale": "Write a character-driven short story with emotional progression and meaningful closure.",
        "Mythology Remix": "Blend mythology motifs with modern situations in a respectful and imaginative way.",
        "Personal Memoir": "Write with reflective tone focused on growth, memory, and inner voice.",
        "Flash Fiction": "Write compact flash fiction with clarity and a satisfying twist ending.",
        "Sci-Fi Masque": "Write a theatrical sci-fi story with masked identities, atmosphere, and futuristic wonder.",
        "Custom": "Write a vivid, engaging story based on the topic and creative cues.",
    }


def get_audience_instruction(audience: str) -> str:
    if audience == "Kids (8+)":
        return "Use simple words, gentle scenes, and fully family-safe storytelling."
    if audience == "Teens":
        return "Use energetic style, emotional depth, and no explicit content."
    if audience == "Family":
        return "Keep it universally suitable, warm, and clean for all age groups."
    return "Keep language tasteful and avoid graphic content."


def build_pdf_bytes(story: str, mode: str, topic: str, audience: str) -> bytes:
    packet = BytesIO()
    doc = SimpleDocTemplate(packet, pagesize=letter)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    title = styles["Title"]

    parts = [
        Paragraph("Arcanova AI Story Export", title),
        Spacer(1, 10),
        Paragraph(f"Mode: {mode}", normal),
        Paragraph(f"Audience: {audience}", normal),
        Paragraph(f"Topic: {topic}", normal),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal),
        Spacer(1, 12),
        Paragraph(story.replace("\n", "<br/>"), normal),
    ]
    doc.build(parts)
    packet.seek(0)
    return packet.read()


def local_fallback_story(topic: str, mode: str, audience: str) -> str:
    openings = [
        f"In a city lit by violet skies, the story of {topic} began quietly.",
        f"Everyone believed they knew {topic}, until one impossible night changed everything.",
        f"At the edge of tomorrow, {topic} became the key to a hidden truth.",
    ]
    mids = [
        "A brave decision forced the hero to choose between fear and purpose.",
        "Clues appeared in unexpected places, and each clue deepened the mystery.",
        "When hope seemed lost, a small act of kindness changed the direction of events.",
    ]
    endings = [
        "By dawn, the world had not become perfect, but it had become better, and that was enough.",
        "The final revelation did not end the journey; it gave everyone a reason to begin again.",
        "What started as a question became a promise: this story would inspire many more to come.",
    ]

    tone_line = f"Mode: {mode}. Audience profile: {audience}."
    return "\n\n".join([random.choice(openings), tone_line, random.choice(mids), random.choice(endings)])


@st.cache_resource
def load_qwen_engine(model_name: str, use_4bit: bool):
    cfg = Config()
    cfg.qwen_model = model_name
    cfg.use_4bit = use_4bit
    return QwenEngine(cfg)


@st.cache_resource
def load_tts_engine():
    return TTSEngine(Config())


if "story" not in st.session_state:
    st.session_state.story = ""
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "mode" not in st.session_state:
    st.session_state.mode = "Character Tale"
if "audience" not in st.session_state:
    st.session_state.audience = "Family"
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = b""
if "count" not in st.session_state:
    st.session_state.count = 0

mode_map = get_mode_instructions()
cfg = Config()

title_col, stats_col = st.columns([3, 1])
with title_col:
    st.markdown("# Arcanova AI Story Narration Studio")
    st.markdown("<span class='tag-chip'>Dark Purple + Pure White</span><span class='tag-chip'>No API Key</span><span class='tag-chip'>Interactive Generation</span>", unsafe_allow_html=True)
with stats_col:
    st.markdown("<div class='panel'><h3 style='color:#1b1036 !important'>Session</h3><p style='color:#1b1036 !important'>Stories: {}</p></div>".format(st.session_state.count), unsafe_allow_html=True)

with st.sidebar:
    st.header("Creative Controls")
    model_name = st.selectbox("Qwen model", ["Qwen/Qwen2.5-3B-Instruct", "Qwen/Qwen2.5-3B"], index=0)
    use_4bit = st.checkbox("Use 4-bit loading (best for T4)", value=True)
    mode = st.selectbox("Story mode", list(mode_map.keys()), index=0)
    audience = st.selectbox("Audience", ["Kids (8+)", "Teens", "Family", "Adults"], index=2)
    max_tokens = st.slider("Story length", 120, 900, cfg.default_max_tokens, 20)
    temperature = st.slider("Creativity", 0.2, 1.3, cfg.default_temperature, 0.1)
    top_p = st.slider("Top-p", 0.5, 1.0, cfg.default_top_p, 0.05)

    st.subheader("Narration")
    tts_engine = load_tts_engine()
    voice = st.selectbox("Voice", tts_engine.get_available_voices(), index=0)
    speed = st.slider("Voice speed", 0.7, 1.4, 1.0, 0.1)
    booming = st.checkbox("Booming effect", value=False)

left, right = st.columns([2, 1])
with left:
    topic = st.text_area(
        "Enter your topic or prompt",
        value=st.session_state.topic,
        placeholder="Example: A masked astronaut uncovers a memory vault on Mars and changes Earth forever.",
        height=170,
    )
with right:
    st.markdown("<div class='panel'><h3 style='color:#1b1036 !important'>How to use</h3><p style='color:#1b1036 !important'>1. Enter topic\n2. Click Generate\n3. Click Narrate\n4. Download</p></div>", unsafe_allow_html=True)

btn1, btn2, btn3 = st.columns(3)
with btn1:
    generate_now = st.button("Generate Story", use_container_width=True)
with btn2:
    narrate_now = st.button("Narrate Full Story", use_container_width=True)
with btn3:
    if st.button("Clear", use_container_width=True):
        st.session_state.story = ""
        st.session_state.audio_bytes = b""
        st.rerun()

if generate_now:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        st.session_state.topic = topic.strip()
        st.session_state.mode = mode
        st.session_state.audience = audience
        prompt = f"Topic: {topic.strip()}"
        system_text = mode_map[mode] + " " + get_audience_instruction(audience) + " Ensure a clear beginning, middle, and ending."

        generated_story = ""
        model_error = None
        try:
            with st.spinner("Generating story with Qwen..."):
                engine = load_qwen_engine(model_name, use_4bit)
                messages = engine.build_prompt(prompt, system_text)
                generated_story = engine.generate_story(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                ).strip()
        except Exception as err:
            model_error = str(err)

        if not generated_story:
            generated_story = local_fallback_story(topic.strip(), mode, audience)
            if model_error:
                st.info("Model was unavailable, so local fallback generation was used for now.")

        st.session_state.story = generated_story
        st.session_state.audio_bytes = b""
        st.session_state.count += 1
        st.success("Story generated.")

if narrate_now:
    if not st.session_state.story.strip():
        st.warning("Generate a story first.")
    else:
        try:
            with st.spinner("Narrating full story..."):
                st.session_state.audio_bytes = tts_engine.generate_audio(
                    st.session_state.story,
                    voice=voice,
                    speed=speed,
                    booming=booming,
                )
            st.success("Narration completed.")
        except Exception as err:
            st.error(f"Narration failed: {err}")

if st.session_state.story:
    st.subheader("Generated Story")
    st.markdown(
        f"<div class='story-box'>{st.session_state.story.replace(chr(10), '<br/>')}</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.audio_bytes:
        st.subheader("Narration")
        st.audio(st.session_state.audio_bytes, format="audio/wav")

    pdf_bytes = build_pdf_bytes(
        st.session_state.story,
        st.session_state.mode,
        st.session_state.topic,
        st.session_state.audience,
    )
    txt_bytes = (
        f"Mode: {st.session_state.mode}\n"
        f"Audience: {st.session_state.audience}\n"
        f"Topic: {st.session_state.topic}\n"
        f"Generated: {datetime.now().isoformat()}\n\n"
        f"{st.session_state.story}\n"
    ).encode("utf-8")

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("Download TXT", data=txt_bytes, file_name="arcanova_story.txt", mime="text/plain", use_container_width=True)
    with d2:
        st.download_button("Download PDF", data=pdf_bytes, file_name="arcanova_story.pdf", mime="application/pdf", use_container_width=True)
    with d3:
        if st.session_state.audio_bytes:
            st.download_button("Download WAV", data=st.session_state.audio_bytes, file_name="arcanova_narration.wav", mime="audio/wav", use_container_width=True)

st.caption("Arcanova AI: dark purple + pure white interactive studio with local generation and narration.")
