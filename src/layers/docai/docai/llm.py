import json

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


class OpenAIClient:
    def __init__(self):
        config = utils.Config()
        secrets = json.loads(config.get_secret("/env/openai/secret/name"))
        self.__headers = {
            "Authorization": secrets["OPENAI_API_KEY"],
            "Content-Type": "application/json",
        }

        self.__url = secrets["OPENAI_API_URL"]

    def __unwrap(self, response: dict, schema: dict) -> dict:
        data = response["choices"][0]["message"]["content"]
        return utils.validate_data(data, schema["schema_definition"])

    def __call_api(self, model: str, messages: list[dict]) -> dict:
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

    def __prepare_messages(
        self, schema_data: dict, text_data: str, image_data: list[dict]
    ) -> list[dict]:
        contents = (
            [
                {
                    "type": "text",
                    "text": c.USER_INSTRUCTIONS_FORMAT.format(
                        schema=schema_data, content=text_data
                    ),
                },
                *image_data,
            ],
        )
        messages: list[dict] = [
            {"role": "system", "content": c.SYSTEM_MESSAGE},
            {"role": "user", "content": contents},
        ]

        return messages

    def __call__(
        self, document: models.DocumentModel, schema: dict, unwrap: bool = True
    ) -> dict:
        schema_data = schema["schema_definition"]
        text_data = document.content if document.is_text() else ""

        image_data = []
        if document.is_pdf():
            image_data = [
                {"type": "image_url", "image_url": {"url": data}}
                for data in utils.load_pdf(document.content)
            ]
        elif document.is_image():
            image_data = [
                {"type": "image_url", "image_url": {"url": data}}
                for data in utils.load_image(document.content)
            ]

        messages = self.__prepare_messages(schema_data, text_data, image_data)
        model = c.VISION_MODEL if image_data else c.TEXT_MODEL

        response = self.__call_api(model, messages)
        if unwrap:
            return self.__unwrap(response, schema)
        return response
