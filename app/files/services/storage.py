from django.core.files.storage import default_storage
from django.core.files.base import File
from django.contrib.auth.models import AbstractBaseUser

import dataclasses

from ..models import UserFile
from .utils import *

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".docx"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

@dataclasses.dataclass
class UploadValidationResult:
    ok: bool
    warnings: list[str] = dataclasses.field(default_factory=list)
    errors: list[str] = dataclasses.field(default_factory=list)

def validate_upload(owner: AbstractBaseUser, uploadde_file) -> UploadValidationResult:
    pass


def save_file(owner: AbstractBaseUser, file: File, description: str) -> UserFile:
    """
    업로드된 파일을 스토리지에 저장하고, 데이터베이스에 파일 정보를 기록(UserFile 객체 생성)합니다.

    Args:
        user (AbstractBaseUser): 파일을 업로드하는 사용자 객체
        file (File): 업로드된 파일 객체 (예: UploadedFile)
        description (str): 사용자가 입력한 파일 설명

    Returns:
        UserFile: 데이터베이스에 생성된 UserFile 모델 인스턴스
    """
    sha256 = calculate_sha256(file)
    file.seek(0) # 파일 포인터를 파일의 시작으로 이동
    path = save_file_path(file)

    obj = UserFile.objects.create(
        owner=owner,
        file=path,
        description=description,
        original_name=file.name,
        size=file.size,
        mime_type=file.content_type,
        sha256=sha256,
    )
    return obj


def save_file_path(file: File) -> str:
    """
    파일의 고유한 이름을 생성하고 Django의 기본 스토리지를 사용하여 저장합니다.

    Args:
        file (File): 저장할 파일 객체

    Returns:
        str: 스토리지 내에 저장된 파일의 경로 (파일명)
    """
    name = generate_unique_name(file.name)
    # django storage의 파일 추상화 도구. settings.py에서 위치 수정, 중복 파일 이름 자동변경
    path = default_storage.save(name, file)
    return path


def delete_file(file):
    pass

def open_file(file):
    pass

def get_download_response(file):
    pass

def get_file(file):
    pass

def get_files(user):
    pass