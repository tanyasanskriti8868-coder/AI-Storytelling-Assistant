from datetime import datetime
from io import BytesIO
import json

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
    --bg0: #fdfbff;
    --bg1: #f5efff;
    --panel: #ffffff;
    --primary: #6f2cff;
    --primary-2: #8d5bff;
    --text: #2a1959;
    --muted: #6f63a6;
    --edge: #e2d4ff;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1200px 600px at 15% 0%, #ffffff 0%, transparent 60%),
        radial-gradient(1000px 500px at 85% 100%, #ece0ff 0%, transparent 60%),
        linear-gradient(140deg, var(--bg0) 0%, var(--bg1) 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8f2ff 100%);
    border-right: 1px solid var(--edge);
}

.brand-card {
    border: 1px solid var(--edge);
    background: linear-gradient(130deg, #ffffff 0%, #f2e7ff 100%);
    border-radius: 18px;
    padding: 24px;
    animation: fadeIn 0.6s ease-out;
}

.pulse-chip {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: #f2e7ff;
    color: #5f34d6;
    font-size: 0.84rem;
    border: 1px solid #dbc6ff;
    animation: pulse 2.4s ease-in-out infinite;
}

.story-box {
    border: 1px solid var(--edge);
    background: var(--panel);
    border-radius: 16px;
    padding: 18px;
    line-height: 1.75;
    color: var(--text);
    animation: riseIn 0.5s ease-out;
}

.feedback-box {
    border: 1px dashed #cdb4ff;
    border-radius: 14px;
    padding: 12px;
    background: #fffafd;
}

h1, h2, h3, p, label, span, div {
    color: var(--text);
}

.stButton > button {
    border: 0;
    border-radius: 12px;
    color: #fff;
    font-weight: 700;
    background: linear-gradient(120deg, var(--primary), var(--primary-2));
    box-shadow: 0 8px 20px rgba(111, 44, 255, 0.24);
    transition: transform 0.2s ease, filter 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.06);
}

@keyframes riseIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.03); opacity: 0.85; }
}
</style>
""",
    unsafe_allow_html=True,
)


def get_mode_instructions() -> dict:
    return {
        "Character Tale": "Write a character-driven short story with emotional progression and a hopeful ending.",
        "Mythology Remix": "Blend mythology motifs with modern life and keep the tone imaginative and respectful.",
        "Personal Memoir": "Write with reflective tone focused on personal growth, values, and empathy.",
        "Flash Fiction": "Write short, crisp flash fiction with a clean twist ending and safe language.",
        "Sci-Fi Masque": "Write a theatrical sci-fi narrative with masked identities, future cities, wonder, and mystery.",
        "Custom": "Write a rich, engaging, family-safe story from the user prompt.",
    }


def get_audience_instruction(audience: str) -> str:
    if audience == "Kids (8+)":
        return "Use simple words, gentle themes, and absolutely no graphic, explicit, or frightening content."
    if audience == "Teens":
        return "Use energetic style with emotional depth. Avoid explicit sexual content and graphic violence."
    if audience == "Family":
        return "Keep content universally suitable and positive for mixed-age listeners."
    return "Keep narrative tasteful and non-explicit. Avoid graphic violence and adult-only sexual content."


def build_pdf_bytes(story: str, mode: str, prompt: str, audience: str) -> bytes:
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
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal),
        Paragraph(f"Prompt: {prompt}", normal),
        Spacer(1, 12),
        Paragraph(story.replace("\n", "<br/>"), normal),
    ]
    doc.build(parts)
    packet.seek(0)
    return packet.read()


@st.cache_resource
def load_qwen_engine(model_name: str, use_4bit: bool):
    cfg = Config()
    cfg.qwen_model = model_name
    cfg.use_4bit = use_4bit
    return QwenEngine(cfg)


@st.cache_resource
def load_tts_engine():
    return TTSEngine(Config())


def save_feedback(name: str, rating: int, comment: str, mode: str):
    cfg = Config()
    feedback_file = cfg.output_dir / "feedback.jsonl"
    payload = {
        "time": datetime.now().isoformat(),
        "name": name.strip() or "anonymous",
        "rating": rating,
        "comment": comment.strip(),
        "mode": mode,
    }
    with open(feedback_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def init_state():
    defaults = {
        "story": "",
        "prompt": "",
        "mode": "Character Tale",
        "audience": "Family",
        "audio_bytes": b"",
        "count": 0,
        "auth_ok": False,
        "login_user": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
cfg = Config()
mode_map = get_mode_instructions()

with st.sidebar:
    st.header("Access")
    if not st.session_state.auth_ok:
        user_in = st.text_input("Username", value="")
        pass_in = st.text_input("Password", value="", type="password")
        guest = st.checkbox("Login as guest (read/write features enabled)", value=True)
        if st.button("Login", use_container_width=True):
            if guest or (user_in == cfg.auth_username and pass_in == cfg.auth_password):
                st.session_state.auth_ok = True
                st.session_state.login_user = user_in or "guest"
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.success(f"Logged in as {st.session_state.login_user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.auth_ok = False
            st.rerun()

if not st.session_state.auth_ok:
    st.markdown(
        """
<div class="brand-card">
    <h1>Arcanova AI</h1>
    <p>Login to continue into your storytelling studio.</p>
    <p class="pulse-chip">No API keys required</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    """
<div class="brand-card">
    <h1>Arcanova AI Story Narration Studio</h1>
    <p>Qwen 3B generation + Kokoro narration. Purple-white premium interface built for all age groups.</p>
    <p class="pulse-chip">Smooth mode active</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Generation Settings")
    model_name = st.selectbox(
        "Qwen model",
        ["Qwen/Qwen2.5-3B-Instruct", "Qwen/Qwen2.5-3B"],
        index=0,
    )
    use_4bit = st.checkbox("Use 4-bit loading (recommended for Tesla T4)", value=True)
    mode = st.selectbox("Story mode", list(mode_map.keys()), index=0)
    audience = st.selectbox("Audience safety", ["Kids (8+)", "Teens", "Family", "Adults"], index=2)
    max_tokens = st.slider("Story length", 120, 900, cfg.default_max_tokens, 20)
    temperature = st.slider("Creativity", 0.2, 1.3, cfg.default_temperature, 0.1)
    top_p = st.slider("Top-p", 0.5, 1.0, cfg.default_top_p, 0.05)

    st.subheader("Narration")
    tts_engine = load_tts_engine()
    voice = st.selectbox("Voice", tts_engine.get_available_voices(), index=0)
    speed = st.slider("Voice speed", 0.7, 1.4, 1.0, 0.1)
    booming = st.checkbox("Booming effect", value=False)

    st.caption(f"Stories generated in this session: {st.session_state.count}")

left, right = st.columns([2, 1])

with left:
    prompt = st.text_area(
        "Story prompt",
        value=st.session_state.prompt,
        placeholder="Example: In Neo-Lucknow, a masked astronaut opens a memory vault under the moon.",
        height=170,
    )

with right:
    st.markdown("### Guidance")
    st.write("1. Choose mode and audience.")
    st.write("2. Generate the story.")
    st.write("3. Narrate with full-story voice rendering.")
    st.write("4. Download and sell-ready export.")

row1, row2, row3 = st.columns(3)
with row1:
    generate_now = st.button("Generate Story", use_container_width=True)
with row2:
    narrate_now = st.button("Narrate Full Story", use_container_width=True)
with row3:
    if st.button("Clear", use_container_width=True):
        st.session_state.story = ""
        st.session_state.audio_bytes = b""
        st.rerun()

if generate_now:
    if not prompt.strip():
        st.warning("Please enter a story prompt.")
    else:
        st.session_state.prompt = prompt.strip()
        st.session_state.mode = mode
        st.session_state.audience = audience

        full_system = (
            mode_map[mode]
            + " "
            + get_audience_instruction(audience)
            + " Ensure coherent beginning, middle, and ending."
        )

        try:
            with st.spinner("Generating story with Qwen..."):
                engine = load_qwen_engine(model_name, use_4bit)
                messages = engine.build_prompt(
                    user_prompt=prompt.strip(),
                    mode_prompt=full_system,
                )
                generated_story = engine.generate_story(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )
            st.session_state.story = generated_story.strip()
            st.session_state.audio_bytes = b""
            st.session_state.count += 1
            st.success("Story generated successfully.")
        except Exception as err:
            st.error(f"Generation failed: {err}")

if narrate_now:
    if not st.session_state.story.strip():
        st.warning("Generate a story first.")
    else:
        try:
            with st.spinner("Narrating full story. This may take a minute for long stories..."):
                audio = tts_engine.generate_audio(
                    st.session_state.story,
                    voice=voice,
                    speed=speed,
                    booming=booming,
                )
            st.session_state.audio_bytes = audio
            st.success("Narration completed for full story.")
        except Exception as err:
            st.error(f"Narration failed: {err}")

if st.session_state.story:
    st.subheader("Generated Story")
    st.markdown(
        f"<div class='story-box'>{st.session_state.story.replace(chr(10), '<br/>')}</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.audio_bytes:
        st.subheader("Narration Output")
        st.audio(st.session_state.audio_bytes, format="audio/wav")

    pdf_bytes = build_pdf_bytes(
        st.session_state.story,
        st.session_state.mode,
        st.session_state.prompt,
        st.session_state.audience,
    )

    txt_bytes = (
        f"Mode: {st.session_state.mode}\n"
        f"Audience: {st.session_state.audience}\n"
        f"Prompt: {st.session_state.prompt}\n"
        f"Generated: {datetime.now().isoformat()}\n\n"
        f"{st.session_state.story}\n"
    ).encode("utf-8")

    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button(
            "Download TXT",
            data=txt_bytes,
            file_name="arcanova_story.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="arcanova_story.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with dl3:
        if st.session_state.audio_bytes:
            st.download_button(
                "Download WAV",
                data=st.session_state.audio_bytes,
                file_name="arcanova_narration.wav",
                mime="audio/wav",
                use_container_width=True,
            )

st.markdown("---")
st.subheader("Feedback")
with st.container(border=False):
    st.markdown("<div class='feedback-box'>Tell us what to improve before launch.</div>", unsafe_allow_html=True)
    fb_name = st.text_input("Name (optional)", value="")
    fb_rating = st.slider("Rating", 1, 5, 5)
    fb_comment = st.text_area("Feedback", value="", placeholder="What should be improved for launch?")
    if st.button("Submit Feedback", use_container_width=False):
        if not fb_comment.strip():
            st.warning("Please enter feedback text.")
        else:
            save_feedback(fb_name, fb_rating, fb_comment, st.session_state.mode)
            st.success("Feedback saved. Thank you.")

st.caption("Arcanova AI: purple-white, local, no API keys, GitHub-ready.")
