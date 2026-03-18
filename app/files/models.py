from django.conf import settings
from django.db import models

import uuid
import os

# 노드 타입 ENUM
class NodeType(models.TextChoices):
    FILE = "file", "File"
    FOLDER = "directory", "Directory"

# 파일 상태 ENUM
class FileStatus(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded" # db_value / label
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"

class FileLanguage(models.TextChoices):
    KOREAN = "ko", "Korean"
    ENGLISH = "en", "English"
    CHINESE = "zh", "Chinese"
    JAPANESE = "ja", "Japanese"
    OTHER = "other", "Other"

class FileAIStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


# 파일/디렉토리 객체
class Node(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nodes"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )
    name = models.CharField(max_length=255)
    node_type = models.CharField(
        max_length=20,
        choices=NodeType.choices,
        default=NodeType.FILE
    )
    description = models.TextField(blank=True)
    path = models.CharField(
        max_length=255,
        db_index=True,
        unique=True,
        default="/",
    )

    status = models.CharField(
        max_length=20,
        choices=FileStatus.choices,
        default=FileStatus.UPLOADED,
        db_index=True,
    )

    starred = models.BooleanField(default=False)
    trashed = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "parent"]),
            models.Index(fields=["owner", "trashed"]),
            models.Index(fields=["owner", "node_type"]),
            models.Index(fields=["owner", "-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "parent", "name"],
                name="uniq_node_name_per_parent",
            )
        ]
    
    @property
    def is_file(self):
        return self.node_type == NodeType.FILE
    
    @property
    def is_directory(self):
        return self.node_type == NodeType.FOLDER

    def save(self, *args, **kwargs):
        if self.parent:
            self.path = f"{self.parent.path}/{self.name}"
        else:
            self.path = f"/{self.name}"
        super().save(*args, **kwargs)
    
    def move(self, new_name=None, new_parent=None):
        old_path = self.path
        
        if new_name:
            self.name = new_name
        if new_parent:
            self.parent = new_parent
        
        if self.parent:
            new_path = f"{self.parent.path}/{self.name}"
        else:
            new_path = f"/{self.name}"
        
        with transaction.atomic():
            if old_path != new_path:
                Node.objects.filter(path__startswith=old_path + "/").update(
                    path=models.functions.Replace(
                        "path",
                        models.Value(old_path + "/"),
                        models.Value(new_path + "/"),
                    )
                )
            
            self.path = new_path
            self.save()


    def __str__(self):
        return f"{self.name} ({self.owner})"


# 실제 파일 저장 위치
def blob_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"blobs/user_{instance.node.owner_id}/{instance.uuid}{ext}"

class FileBlob(models.Model):
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name="blob",
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    file = models.FileField(upload_to=blob_upload_path)
    original_name = models.CharField(max_length=255)

    language = models.CharField(
        max_length=32,
        choices=FileLanguage.choices,
        default=FileLanguage.ENGLISH,
    )
    mime_type = models.CharField(max_length=100, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    sha256 = models.CharField(max_length=64, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def size_mb(self):
        if self.size is None:
            return None
        return round(self.size / 1024 / 1024, 2)

    def __str__(self):
        return f"{self.original_name}"


class FileAI(models.Model):
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name="ai",
    )
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=32, choices=FileLanguage.choices, default=FileLanguage.KOREAN)

    parse_status = models.CharField(
        max_length=20,
        choices=FileAIStatus.choices,
        default=FileAIStatus.PENDING,
    )
    embedding_status = models.CharField(
        max_length=20,
        choices=FileAIStatus.choices,
        default=FileAIStatus.PENDING,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.node.name} - AI Info"


class FileEmbedding(models.Model):
    file_ai = models.ForeignKey(
        FileAI,
        on_delete=models.CASCADE,
        related_name="embeddings",
    )
    vector = models.JSONField()
    model_name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_ai.node.name} - {self.model_name}"

class UserStorage(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="storage",
    )
    total_size = models.BigIntegerField(default=0)
    used_size = models.BigIntegerField(default=0)
    remaining_size = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Storage"