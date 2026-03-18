from django.core.files.storage import default_storage
from django.core.files.base import File
from django.contrib.auth.models import AbstractBaseUser

import dataclasses
import os

from ..models import UserFile
from .utils import *

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".docx", ".html"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

@dataclasses.dataclass
class UploadValidationResult:
    ok: bool
    warnings: list[str] = dataclasses.field(default_factory=list)
    errors: list[str] = dataclasses.field(default_factory=list)
    duplicate: bool = False

def validate_upload(owner: AbstractBaseUser, uploaded_file: File) -> UploadValidationResult:
    """
    파일 업로드 전 유효성을 검사합니다.

    Args:
        owner (AbstractBaseUser): 파일을 업로드하는 사용자 객체
        uploaded_file (File): 업로드된 파일 객체 (예: UploadedFile)
    
    기능:
        - 파일 크기 검사
        - 파일 형식/MIME 타입 검사
        - 파일 중복 검사

    Returns:
        UploadValidationResult: 유효성 검사 결과
    """
    warnings = []
    errors = []

    if uploaded_file is None:
        return UploadValidationResult(
            ok=False,
            errors=["파일이 없습니다."]
        )
    
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        return UploadValidationResult(
            ok=False,
            errors=["파일 크기가 제한을 초과했습니다."]
        )

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return UploadValidationResult(
            ok=False,
            errors=["지원하지 않는 파일 형식입니다."]
        )

    content_type = getattr(uploaded_file, "content_type", None)
    if not content_type:
        warnings.append("파일의 MIME을 확인할 수 없습니다.")
    
    sha256 = calculate_sha256(uploaded_file)
    duplicate = UserFile.objects.filter(owner=owner, sha256=sha256).exists()
    if duplicate:
        warnings.append("이미 존재하는 파일입니다.")
    
    ok = len(errors) == 0

    return UploadValidationResult(
        ok=ok,
        warnings=warnings,
        errors=errors,
        duplicate=duplicate,
    )


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
    file.seek(0)

    # 중복 파일 저장 방지
    # existing = UserFile.objects.filter(owner=owner, sha256=sha256).first()
    # if existing:
    #     return existing
    
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