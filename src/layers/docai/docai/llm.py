import json
from typing import Any

import requests

from docai import constants as c
from docai import models, utils


def is_image(mime_type: str) -> bool:
    return mime_type in (
        models.MimeTypeEnum.PNG.value,
        models.MimeTypeEnum.JPG.value,
        models.MimeTypeEnum.JPEG.value,
        models.MimeTypeEnum.GIF.value,
        models.MimeTypeEnum.BMP.value,
        models.MimeTypeEnum.TIFF.value,
    )


def is_pdf(mime_type: str) -> bool:
    return mime_type == models.MimeTypeEnum.PDF.value


def is_text(mime_type: str) -> bool:
    return mime_type == models.MimeTypeEnum.TXT.value


def load_media(content: str, mime_type: str) -> list[str]:
    if is_pdf(mime_type):
        return utils.load_pdf(content)
    if is_image(mime_type):
        return utils.load_image(content)
    return []


class OpenAIClient:
    def __init__(self):
        config = utils.Config()
        secrets_raw = config.get_secret("/env/openai/secret/name")
        secrets = json.loads(secrets_raw)

        self.__headers = {
            "Authorization": secrets["OPENAI_API_KEY"],
            "Content-Type": "application/json",
        }

        self.__url = secrets["OPENAI_API_URL"]

    def __unwrap(self, response: dict, schema: dict) -> dict:
        data = response["choices"][0]["message"]["content"]
        return utils.validate_data(data, schema["schema_definition"])

    def __call_api(self, model: str, messages: list[object]) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "seed": c.SEED,
            "temperature": c.TEMPERATURE,
            "max_tokens": c.MAX_OUTPUT_TOKENS,
        }
        response = requests.post(self.__url, headers=self.__headers, json=payload)
        response.raise_for_status()
        return response.json()

    def __call__(
        self, document: dict[str, str], schema: dict[str, str], unwrap: bool = True
    ) -> dict:
        schema_data = schema["schema_definition"]
        mime_type = document["mime_type"]
        content = document["content"] if is_text(mime_type) else ""

        text = c.USER_INSTRUCTIONS_FORMAT.format(schema=schema_data, content=content)
        text_content = {"type": "text", "text": text}
        image_content = [
            {"type": "image_url", "image_url": {"url": image}}
            for image in load_media(content, mime_type)
        ]
        user_content = [text_content, *image_content]
        messages = [
            {"role": "system", "content": c.SYSTEM_MESSAGE},
            {"role": "user", "content": user_content},
        ]

        model = c.TEXT_MODEL
        if image_content:
            model = c.VISION_MODEL

        response = self.__call_api(model, messages)
        if unwrap:
            return self.__unwrap(response, schema)
        return response
