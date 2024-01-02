from docai import exceptions as exc
from docai import models


def process_error(e: Exception) -> dict:
    """Process an exception and return a dict"""
    if e in exc.EXCEPTIONS:
        status_code = 400
        message = str(e)
    else:
        status_code = 500
        message = "Internal Server Error"

    body = models.ErrorResponseModel(
        error=models.ErrorModel(name=e.__class__.__name__, message=message)
    ).json()
    return {"statusCode": status_code, "body": body}
