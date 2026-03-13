import hashlib
import uuid
import os

def calculate_sha256(file):
    sha256 = hashlib.sha256()

    for chunk in file.chunks():
        sha256.update(chunk)
    return sha256.hexdigest()

def generate_unique_name(name):
    ext = os.path.splitext(name)[1]
    return f"uploads/{uuid.uuid4()}{ext}"