import hashlib
import uuid
import os

def calculate_sha256(file):
    sha256 = hashlib.sha256()

    file.seek(0)

    for chunk in file.chunks():
        sha256.update(chunk)

    file.seek(0)
    
    return sha256.hexdigest()

def extract_ext(name):
    return os.path.splitext(name)[1]


def generate_unique_name(name):
    ext = extract_ext(name)
    return f"uploads/{uuid.uuid4()}{ext}"
