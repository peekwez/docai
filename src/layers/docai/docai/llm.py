from typing import Any

import boto3
from openai import OpenAI

from docai import constants as c
from docai import stream, utils


class LLMClient:
    def __init__(
        self,
        api_key: str,
    ):
        self.__openai = OpenAI(api_key=api_key)

    def __unwrap_response(self, response: dict, schema_definition: dict) -> dict:
        valid_data = utils.validate_data(
            response["choices"][0]["message"]["content"], schema_definition
        )
        return {"result": valid_data, "metadata": response["usage"]}

    def __call_api(
        self, schema_definition: dict, model: str, messages: Any, images: dict
    ) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "seed": c.SEED,
            "temperature": c.TEMPERATURE,
            "max_tokens": c.MAX_OUTPUT_TOKENS,
        }
        data = {"request": payload, "images": images, "error": None}
        completion = self.__openai.chat.completions.create(**payload)
        response = self.__unwrap_response(completion.dict(), schema_definition)
        data.update(response)
        return data

    def __call__(
        self,
        schema_definition: dict,
        text_data: str,
        s3: boto3.client,
        bucket_name: str,
        image_list: list[str] | None = None,
    ) -> dict:
        images = {}
        text = c.USER_INSTRUCTIONS_FORMAT.format(
            schema=schema_definition, content=text_data
        )

        user_content: list[dict[str, dict | str]] = [{"type": "text", "text": text}]
        if image_list:
            images = stream.generate_presigned_url(s3, bucket_name, image_list)
            for _, url in images.items():
                user_content.append({"type": "image_url", "image_url": {"url": url}})

        messages = [
            {"role": "system", "content": c.SYSTEM_MESSAGE},
            {"role": "user", "content": user_content},
        ]

        model = c.VISION_MODEL if images else c.TEXT_MODEL
        return self.__call_api(schema_definition, model, messages, images)
