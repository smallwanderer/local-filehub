from django.conf import settings
from django.db import models

# 파일 상태 ENUM
class FileStatus(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded" # db_value / label
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"


# 사용자 파일 메타데이터
class UserFile(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_files"
    )
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    original_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    mime_type = models.CharField(max_length=100, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    sha256 = models.CharField(max_length=64, blank=True, null=True, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=FileStatus.choices,
        default=FileStatus.UPLOADED,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
        ]
    
    def is_ready(self):
        return self.status == FileStatus.READY

    def size_mb(self):
        if self.size is None:
            return 0
        return round(self.size / 1024 / 1024, 2)

    def __str__(self):
        return f"{self.original_name} ({self.owner})"


# 파일 상태 필드




# 텍스트 추출
class FileTextContext(models.Model):
    pass


# 파일 벡터 스토어
class FileEmbedding(models.Model):
    pass