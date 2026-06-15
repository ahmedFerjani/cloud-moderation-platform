from io import BytesIO

from PIL import Image

from common.exceptions import APPError
from constants import ALLOWED_IMAGE_TYPES, MAX_UPLOAD_SIZE_BYTES


def validate_upload_size(object_size: int):

    if object_size <= 0:
        raise APPError("INVALID_OBJECT_SIZE", "Uploaded object is empty", 400)

    if object_size > MAX_UPLOAD_SIZE_BYTES:
        raise APPError(
            "UPLOAD_TOO_LARGE",
            f"Uploaded object exceeds max size of {MAX_UPLOAD_SIZE_BYTES} bytes",
            400,
        )


def validate_image(image_data: bytes) -> str:

    try:

        image = Image.open(BytesIO(image_data))

        image_type = (image.format or "").lower()

    except Exception:

        raise APPError("INVALID_IMAGE_FILE", "Invalid image file", 400)

    if image_type not in ALLOWED_IMAGE_TYPES:

        raise APPError("UNSUPPORTED_IMAGE_TYPE", "Unsupported image type", 400)

    return image_type
