import os
import sys
from pathlib import Path
import django

project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(project_root))

# Django settings 모듈 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django 초기화
django.setup()

from document_ai.parsers.docling_parser import parse_document_entry, ParseResult

sample_file = project_root / "tests" / "test_files" / "hwpx_test.hwpx"

if not sample_file.exists():
    raise FileNotFoundError(f"Test file not found: {sample_file}")

result = parse_document_entry(str(sample_file))

output_file = project_root / "tests" / "test_files" / "hwpx_test_result.json"
output_file.write_text(result.model_dump_json(indent=2), encoding="utf-8")