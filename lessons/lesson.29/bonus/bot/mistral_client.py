from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

try:
    from mistralai import Mistral  # type: ignore
except Exception:
    Mistral = None  # type: ignore

try:
    from mistralai.client import Mistral as LegacyMistral  # type: ignore
except Exception:
    LegacyMistral = None  # type: ignore


SYSTEM_PROMPT = """
Ты дружелюбный ассистент CRM-бота.
Нужно извлечь данные для создания лида и вернуть СТРОГО JSON:
{
  "action": "create_lead" | "none",
  "args": {
    "name": "... или пусто",
    "phone": "... или пусто",
    "email": "... или пусто",
    "comment": "... или пусто",
    "source": "telegram-mcp-bot"
  },
  "reply": "дружелюбный ответ пользователю"
}

Правила:
- Обязательные поля: name, phone, email.
- comment опционален.
- Если обязательных данных хватает, верни action=create_lead.
- Если не хватает, верни action=none и заполни в args все, что удалось извлечь.
- Никакого текста вне JSON.
""".strip()

logger = logging.getLogger(__name__)


class MistralClient:
    def __init__(self, api_key: str, model: str = "mistral-medium-latest", timeout: float = 25.0) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip() or "mistral-medium-latest"
        self.timeout = timeout
        self.default_model = "mistral-medium-latest"

    def _request_with_model(self, model_name: str, user_text: str) -> str:
        if Mistral is not None:
            client = Mistral(api_key=self.api_key, timeout_ms=int(self.timeout * 1000))
            response = client.chat.complete(
                model=model_name,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
            )
            choices = getattr(response, "choices", None) or []
            message = getattr(choices[0], "message", None) if choices else None
            return (getattr(message, "content", None) or "").strip()

        if LegacyMistral is not None:
            client = LegacyMistral(api_key=self.api_key)
            response = client.chat.complete(
                model=model_name,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
            )
            choices = getattr(response, "choices", None) or []
            message = getattr(choices[0], "message", None) if choices else None
            return (getattr(message, "content", None) or "").strip()

        raise RuntimeError("No compatible mistralai client found")

    def _fallback_parse(self, user_text: str) -> dict[str, Any]:
        text = user_text.strip()

        if text.startswith("/lead"):
            text = text[len("/lead") :].strip()
        parts = [p.strip() for p in text.split(";")]
        if len(parts) >= 3:
            return {
                "action": "create_lead",
                "args": {
                    "name": parts[0],
                    "phone": parts[1],
                    "email": parts[2],
                    "comment": parts[3] if len(parts) >= 4 else "",
                    "source": "telegram-mcp-bot",
                },
                "reply": "Отлично, обрабатываю заявку и передаю в CRM.",
            }

        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phone_match = re.search(r"\+?\d[\d\-\s()]{8,}\d", text)
        extracted_name = ""
        name_match = re.search(r"(?:меня зовут|я)\s+([A-Za-zА-Яа-яЁё\-]{2,})", text, flags=re.IGNORECASE)
        if name_match:
            extracted_name = name_match.group(1).strip()

        return {
            "action": "none",
            "args": {
                "name": extracted_name,
                "phone": phone_match.group(0).strip() if phone_match else "",
                "email": email_match.group(0).strip() if email_match else "",
                "comment": text if text and not (email_match or phone_match or extracted_name) else "",
                "source": "telegram-mcp-bot",
            },
            "reply": (
                "С радостью помогу оформить лид. "
                "Поделитесь, пожалуйста, именем, телефоном и email. "
                "Комментарий можно добавить по желанию."
            ),
        }

    def _normalize_json_text(self, content: str) -> str:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json|JSON)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()
        return text

    def decide_action(self, user_text: str, current_draft: dict[str, str] | None = None) -> dict[str, Any]:
        logger.info("LLM input text: %s", user_text)
        if not self.api_key:
            logger.warning("MISTRAL_API_KEY is empty, using fallback parser")
            return self._fallback_parse(user_text)
        context_json = json.dumps(current_draft or {}, ensure_ascii=False)
        user_with_context = (
            f"Текущее состояние анкеты (уже собрано): {context_json}\n"
            f"Новое сообщение пользователя: {user_text}"
        )

        try:
            logger.info("LLM request: model=%s, provider=mistral", self.model)
            content = self._request_with_model(self.model, user_with_context)
        except Exception as err:
            err_text = str(err).lower()
            if "invalid model" in err_text and self.model != self.default_model:
                logger.warning(
                    "Configured model '%s' is invalid, retrying with '%s'",
                    self.model,
                    self.default_model,
                )
                try:
                    content = self._request_with_model(self.default_model, user_with_context)
                except Exception as err2:
                    logger.exception("LLM fallback model request failed, using parser fallback: %s", err2)
                    return self._fallback_parse(user_text)
            else:
                logger.exception("LLM request failed, using fallback parser: %s", err)
                return self._fallback_parse(user_text)

        if not content:
            logger.warning("LLM response content is empty, using fallback parser")
            return self._fallback_parse(user_text)
        logger.info("LLM raw response content: %s", content)

        try:
            normalized = self._normalize_json_text(content)
            parsed = json.loads(normalized)
            if not isinstance(parsed, dict):
                raise ValueError("response is not object")
            logger.info("LLM parsed decision: %s", parsed)
            return parsed
        except Exception as err:
            logger.warning("LLM response is not valid JSON (%s), using fallback parser", err)
            return self._fallback_parse(user_text)


def build_mistral_client_from_env() -> MistralClient:
    return MistralClient(
        api_key=os.getenv("MISTRAL_API_KEY", ""),
        model=os.getenv("MISTRAL_MODEL", "mistral-medium-latest"),
    )
