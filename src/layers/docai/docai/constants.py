import os

SEED = 43
TEMPERATURE = 0
STAGE = os.environ.get("STAGE", "dev")
TEXT_MODEL = "gpt-4-1106-preview"
VISION_MODEL = "gpt-4-vision-preview"
SCHEMA_TOKEN_LIMIT = 2048
MAX_OUTPUT_TOKENS = 4096

SYSTEM_MESSAGE = """
You are a data extractor. Given a JSON schema and the contents of a plain text or a set of images,
you MUST return ONLY the extracted data based on the schema definition provided. Do not include
any additional text in your response besides the extracted data in JSON format. If you do not
know the answer, you should return an empty string, empty list or null value.
"""

USER_INSTRUCTIONS_FORMAT = """
The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{schema}

Content:
{content}

```"""
