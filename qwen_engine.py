import logging

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


logger = logging.getLogger(__name__)


class QwenEngine:
    """Local Qwen story generation engine (no API keys)."""

    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = config.qwen_model
        self._load_model()

    def _load_model(self):
        logger.info("Loading model: %s", self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            cache_dir=str(self.config.models_dir),
            trust_remote_code=True,
        )

        model_kwargs = {
            "cache_dir": str(self.config.models_dir),
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
            "device_map": "auto" if self.device == "cuda" else None,
        }

        if self.device == "cuda":
            if self.config.use_4bit:
                try:
                    from transformers import BitsAndBytesConfig

                    model_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.float16,
                    )
                except Exception:
                    model_kwargs["torch_dtype"] = torch.float16
            else:
                model_kwargs["torch_dtype"] = torch.float16
        else:
            model_kwargs["torch_dtype"] = torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, **model_kwargs)
        self.model.eval()

    @staticmethod
    def build_prompt(user_prompt: str, mode_prompt: str) -> list:
        return [
            {"role": "system", "content": mode_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def generate_story(
        self,
        messages: list,
        temperature: float = 0.8,
        max_tokens: int = 320,
        top_p: float = 0.9,
    ) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model is not loaded")

        prompt_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt_text, return_tensors="pt")

        if self.device == "cuda":
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                repetition_penalty=1.15,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        input_len = inputs["input_ids"].shape[1]
        generated = output_ids[0][input_len:]
        story = self.tokenizer.decode(generated, skip_special_tokens=True).strip()
        return story