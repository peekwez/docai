from docai import models


def process_error(e: Exception) -> models.ErrorResponseModel:
    """Process an exception and return a dict"""
    error = models.ErrorModel(error_name=e.__class__.__name__, error_message=str(e))
    return models.ErrorResponseModel(error=error)
