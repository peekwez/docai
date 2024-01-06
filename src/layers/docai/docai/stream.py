import base64
import concurrent.futures

import boto3
import fitz

from docai import models, utils

DPI = 300
DEFAULT_IMAGE_FORMAT = "png"
DEFAULT_IMAGE_MIME_TYPE = models.MimeTypeEnum.PNG.value


def is_image(mime_type: str) -> bool:
    """Return True if the mime type is an image."""
    return mime_type in (
        models.MimeTypeEnum.PNG.value,
        models.MimeTypeEnum.JPG.value,
        models.MimeTypeEnum.JPEG.value,
        models.MimeTypeEnum.GIF.value,
        models.MimeTypeEnum.BMP.value,
        models.MimeTypeEnum.TIFF.value,
    )


def is_pdf(mime_type: str) -> bool:
    """Return True if the mime type is PDF."""
    return mime_type == models.MimeTypeEnum.PDF.value


def is_text(mime_type: str) -> bool:
    """Return True if the mime type is text."""
    return mime_type == models.MimeTypeEnum.TXT.value


def load_pdf(data: str) -> list[bytes]:
    """Given a base64 encoded string, return the contents of document into multiple images"""
    decoded = base64.b64decode(data)
    pages = fitz.open(stream=decoded, filetype="pdf")
    images = []
    for page in pages:
        image = page.get_pixmap(dpi=DPI)
        images.append(image.tobytes(output=DEFAULT_IMAGE_FORMAT))
    return images


def load_image(data: str) -> list[bytes]:
    """Given a base64 encoded string, return the contents of the image as a list of base64 string."""
    return [base64.b64decode(data)]


def load_media(content: str, mime_type: str) -> tuple[list[bytes], str]:
    """Given a base64 encoded string, return the contents of the document as a list of bytes and mime type."""
    if is_pdf(mime_type):
        return load_pdf(content), DEFAULT_IMAGE_MIME_TYPE
    if is_image(mime_type):
        return load_image(content), mime_type
    return [], mime_type


def create_key(request_id: str | None = None) -> str:
    """Create a unique key for storing the document in S3."""
    prefix = f"{request_id}/" if request_id else utils.guid()
    return f"{prefix}/{utils.guid()}"


def save_to_s3(
    s3: boto3.client, bucket_name: str, content: bytes, mime_type: str
) -> str:
    """Save the content to S3 and return the key."""
    key = create_key()
    s3.put_object(Bucket=bucket_name, Key=key, Body=content, ContentType=mime_type)
    return key


def save_media(
    s3: boto3.client, bucket_name: str, data: list[bytes], mime_type: str
) -> list[str]:
    """Save the media to S3 and return the keys."""

    def fn(content: bytes) -> str:
        return save_to_s3(s3, bucket_name, content, mime_type)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for content in data:
            futures.append(executor.submit(fn, content))
        return [future.result() for future in concurrent.futures.as_completed(futures)]


def generate_presigned_url(
    s3: boto3.client, bucket_name: str, keys: list[str]
) -> dict[str, str]:
    """Generate a presigned URL for the given keys."""
    return {
        key: s3.generate_presigned_url(
            "get_object", Params=dict(Bucket=bucket_name, Key=key), ExpiresIn=300
        )
        for key in keys
    }


def prepare_extraction_request(
    schema: dict, document: dict, s3: boto3.client, bucket_name: str
) -> dict:
    """Given a schema and document, return a dictionary with the data for the LLM request."""
    schema_data = schema["schema_definition"]
    mime_type = document["mime_type"]

    text_data = document["content"] if is_text(mime_type) else ""
    image_list = None

    data, new_mime_type = load_media(document["content"], mime_type)
    image_list = save_media(s3, bucket_name, data, new_mime_type)

    return dict(
        text_data=text_data, image_list=image_list, schema_definition=schema_data
    )
