from dataclasses import dataclass
from pathlib import Path
import json
import platform


@dataclass
class Config:
    """Runtime configuration for Arcanova AI."""

    qwen_model: str = "Qwen/Qwen2.5-3B-Instruct"
    default_max_tokens: int = 320
    default_temperature: float = 0.8
    default_top_p: float = 0.9
    tts_sample_rate: int = 22050
    use_4bit: bool = True
    auth_username: str = "admin"
    auth_password: str = "admin123"

    def __post_init__(self):
        self.root_dir = Path(__file__).resolve().parent
        self.models_dir = self.root_dir / "models"
        self.output_dir = self.root_dir / "outputs"
        self.stories_dir = self.output_dir / "saved_stories"
        self.audio_dir = self.output_dir / "narrations"
        self.cache_dir = self.root_dir / ".cache"

        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stories_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._load_custom_config()

    def _load_custom_config(self):
        config_path = self.root_dir / "config.json"
        if not config_path.exists():
            return

        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            return

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save_config(self):
        payload = {
            "qwen_model": self.qwen_model,
            "default_max_tokens": self.default_max_tokens,
            "default_temperature": self.default_temperature,
            "default_top_p": self.default_top_p,
            "tts_sample_rate": self.tts_sample_rate,
            "use_4bit": self.use_4bit,
            "auth_username": self.auth_username,
            "auth_password": self.auth_password,
        }
        with open(self.root_dir / "config.json", "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    @staticmethod
    def is_gpu_available() -> bool:
        try:
            import torch

            return torch.cuda.is_available()
        except Exception:
            return False

    @staticmethod
    def get_system_info() -> dict:
        info = {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "gpu_available": Config.is_gpu_available(),
        }
        try:
            import torch

            if info["gpu_available"]:
                info["gpu_name"] = torch.cuda.get_device_name(0)
        except Exception:
            pass
        return info