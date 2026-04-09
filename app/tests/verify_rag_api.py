import os
import django
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

# Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
django.setup()

from files.models import Node, NodeType, FileBlob
from django.contrib.auth import get_user_model
from document_ai.models import DocumentParseResult, ChunkEmbedding
from config.enums import AIStatus

# 1. 테스트 유저 준비
User = get_user_model()
user, _ = User.objects.get_or_create(email="test_rag@example.com", defaults={"password": "testpassword123"})

# 2. 문서 업로드를 위한 Mocking 세팅 및 Celery 동기 실행 우회
# 테스트 환경에서는 delay() 대신 직접 호출이 일어나도록 하거나, sync 동작 권장.
print("1. Creating dummy test file...")

# .hwpx 파일을 업로드하는 시나리오
from files.models import Node

if Node.objects.filter(owner=user, path="/dummy1.hwpx").exists():
    Node.objects.filter(owner=user, path="/dummy1.hwpx").delete()

dummy_file_path = "tests/test_files/dummy1.hwpx"
os.makedirs(os.path.dirname(dummy_file_path), exist_ok=True)
with open(dummy_file_path, "wb") as f:
    f.write(b"Test HWPX Content")

upload_file = SimpleUploadedFile("dummy1.hwpx", b"dummy content", content_type="application/octet-stream")

# 3. 모델을 생성해서 DB와 Signal을 트리거합니다.
from files.services.storage import save_file

with patch('document_ai.task.parse_document_with_docling.delay') as mock_parse_delay:
    node = save_file(
        owner=user,
        file=upload_file,
        description="RAG Search Test File"
    )
    print(f"2. File saved (Node ID: {node.id}). Signal fired.")

    print("node.id =", node.id)

    exists_by_id = Node.objects.filter(id=node.id).exists()
    print("exists_by_id =", exists_by_id)

    saved = Node.objects.filter(id=node.id).values("id", "name", "path", "owner_id").first()
    print("saved row =", saved)
    
    # post_save 시그널이 백그라운드 작업을 delay()로 잘 불렀는지 확인
    if mock_parse_delay.called:
        print("✅ Signal correctly triggered parsing task!")
    else:
        print("❌ Signal DID NOT trigger the parsing task!")

print("\n3. Testing Retrieval Engine & API Manually:")
print("Since Celery is async, we will inject a dummy chunk & embedding to test VectorSearchView")

# 4. 수동으로 ChunkEmbedding 삽입 (검색 로직 테스트용)
from document_ai.models import DocumentParseResult, DocumentChunk

parse_res, _ = DocumentParseResult.objects.get_or_create(
    node=node,
    defaults={
        "parser_name": "docling",
        "status": AIStatus.COMPLETED,
    }
)

chunk = DocumentChunk.objects.create(
    parse_result=parse_res,
    chunk_index=0,
    text="RAG 파이프라인의 검색 엔진 시스템이 정상적으로 완성되었습니다! 이제 HWPX와 모든 문서에서 검색이 가능합니다.",
    status=AIStatus.COMPLETED
)

# bge-m3 1024차원 가짜 더미 벡터 생성 (정규화된 형태)
dummy_vector = [0.01] * 1024 
ChunkEmbedding.objects.create(
    chunk=chunk,
    vector=dummy_vector,
    model_name="BAAI/bge-m3",
    status=AIStatus.COMPLETED
)

print("DEBUG parse result count:", DocumentParseResult.objects.count())
print("DEBUG chunk count:", DocumentChunk.objects.count())
print("DEBUG embedding count:", ChunkEmbedding.objects.count())
print("DEBUG embedding rows:", list(ChunkEmbedding.objects.values("id", "model_name", "status", "chunk_id")))

# 5. API 호출 (REST 뷰 테스트)
client = Client()
client.force_login(user)

response = client.post(
    "/api/document-ai/v1/search/",
    {
        "query": "검색 시스템",
        "top_k": 2
    },
    content_type="application/json"
)

print(f"\n4. RAG API Response Status: {response.status_code}")
if response.status_code == 200:
    import json
    data = response.json()
    print("API Response Data:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(response.content.decode())

# Clean up
input("Press Enter to delete the node...")
node.delete()
