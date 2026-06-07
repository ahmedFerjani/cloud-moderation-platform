import hashlib
import os


def extract_image_id_from_s3_key(object_key: str) -> str:

    filename = object_key.rsplit("/", 1)[-1]
    image_id, _ = os.path.splitext(filename)

    return image_id


def generate_image_hash(image_data: bytes) -> str:

    return hashlib.sha256(image_data).hexdigest()
