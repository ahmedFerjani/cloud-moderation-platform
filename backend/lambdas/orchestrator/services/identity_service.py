import hashlib
import os


def extract_image_id_from_s3_key(object_key: str) -> str:

    filename = object_key.rsplit("/", 1)[-1]
    image_id, _ = os.path.splitext(filename)

    return image_id


def extract_user_id_from_s3_key(object_key: str) -> str | None:
    # uploads/{user_id}/{image_id}.{ext}
    parts = object_key.split("/")
    return parts[1] if len(parts) == 3 else None


def generate_image_hash(image_data: bytes) -> str:

    return hashlib.sha256(image_data).hexdigest()
