import io
import os
import tempfile
import wave
import logging

import numpy as np


logger = logging.getLogger(__name__)


class TTSEngine:
    """Offline TTS engine preferring Kokoro, with pyttsx3 fallback."""

    def __init__(self, config):
        self.config = config
        self.backend = None
        self.kokoro = None
        self.voice_labels = ["English", "English (Soft)", "Hindi"]
        self._setup_backend()

    def _setup_backend(self):
        try:
            from kokoro import KokoroTTS  # type: ignore

            self.kokoro = KokoroTTS()
            self.backend = "kokoro"
            return
        except Exception:
            self.backend = "pyttsx3"

    def get_available_voices(self):
        return self.voice_labels

    def generate_audio(
        self,
        text: str,
        voice: str = "English",
        speed: float = 1.0,
        booming: bool = False,
    ) -> bytes:
        if not text.strip():
            raise ValueError("Text for narration cannot be empty")

        parts = self._chunk_text(text)
        rendered = []

        for piece in parts:
            if self.backend == "kokoro" and self.kokoro is not None:
                try:
                    rendered.append(self._kokoro_to_wav_bytes(piece))
                    continue
                except Exception as err:
                    logger.warning("Kokoro failed for chunk, fallback to pyttsx3: %s", err)

            rendered.append(self._pyttsx3_to_wav_bytes(piece, voice=voice, speed=speed))

        merged = self._merge_wav_segments(rendered)
        if booming:
            merged = self._apply_booming_effect(merged)
        return merged

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 380) -> list:
        cleaned = " ".join(text.split())
        if len(cleaned) <= max_chars:
            return [cleaned]

        chunks = []
        current = []
        current_len = 0
        for sentence in cleaned.replace("!", "! ").replace("?", "? ").split(". "):
            sent = sentence.strip()
            if not sent:
                continue
            if not sent.endswith((".", "!", "?")):
                sent = sent + "."
            if current_len + len(sent) > max_chars and current:
                chunks.append(" ".join(current).strip())
                current = [sent]
                current_len = len(sent)
            else:
                current.append(sent)
                current_len += len(sent)
        if current:
            chunks.append(" ".join(current).strip())
        return chunks

    def _kokoro_to_wav_bytes(self, text: str) -> bytes:
        generated = self.kokoro.generate(text)

        if isinstance(generated, bytes):
            return generated

        audio = np.asarray(generated, dtype=np.float32)
        audio = np.clip(audio, -1.0, 1.0)
        pcm = (audio * 32767.0).astype(np.int16).tobytes()

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.config.tts_sample_rate)
            wav_file.writeframes(pcm)

        return buffer.getvalue()

    def _pyttsx3_to_wav_bytes(self, text: str, voice: str, speed: float) -> bytes:
        import pyttsx3

        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        if voices:
            target = "hi" if "Hindi" in voice else "en"
            selected = voices[0].id
            for item in voices:
                name = str(getattr(item, "name", "")).lower()
                langs = str(getattr(item, "languages", "")).lower()
                if target in name or target in langs:
                    selected = item.id
                    break
            engine.setProperty("voice", selected)

        engine.setProperty("rate", int(165 * max(0.6, min(1.6, speed))))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name

        try:
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            with open(tmp_path, "rb") as fh:
                return fh.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @staticmethod
    def _merge_wav_segments(wavs: list) -> bytes:
        if not wavs:
            raise ValueError("No WAV segments to merge")
        if len(wavs) == 1:
            return wavs[0]

        all_frames = []
        params = None
        for blob in wavs:
            with wave.open(io.BytesIO(blob), "rb") as wf:
                if params is None:
                    params = wf.getparams()
                all_frames.append(wf.readframes(wf.getnframes()))

        out = io.BytesIO()
        with wave.open(out, "wb") as ww:
            ww.setparams(params)
            for frames in all_frames:
                ww.writeframes(frames)
        return out.getvalue()

    @staticmethod
    def _apply_booming_effect(wav_bytes: bytes) -> bytes:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        if sample_width != 2 or channels != 1:
            return wav_bytes

        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

        # Light low-frequency emphasis + controlled gain for a "booming" voice texture.
        kernel = np.ones(9, dtype=np.float32) / 9.0
        low_band = np.convolve(audio, kernel, mode="same")
        mixed = (0.68 * audio) + (0.48 * low_band)
        mixed = mixed * 1.12
        mixed = np.clip(mixed, -32768, 32767).astype(np.int16)

        out = io.BytesIO()
        with wave.open(out, "wb") as ww:
            ww.setnchannels(channels)
            ww.setsampwidth(sample_width)
            ww.setframerate(frame_rate)
            ww.writeframes(mixed.tobytes())

        return out.getvalue()