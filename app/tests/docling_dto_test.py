import os

import pytest
from types import SimpleNamespace

from document_ai.parsers.docling_parser import _parse_docling_document, ParseResult


class FakeTokenizer:
    def count_tokens(self, text: str) -> int:
        return len(text.split())


class FakeChunker:
    def chunk(self, document):
        return [
            SimpleNamespace(
                meta={"section": "intro"},
            ),
            SimpleNamespace(
                meta={"section": "body"},
            ),
        ]

    def contextualize(self, chunk):
        if chunk.meta["section"] == "intro":
            return "This is intro chunk"
        return "This is body chunk"


class FakeStatus:
    value = "SUCCESS"


class FakeVersion:
    docling_version = "1.0.0"
    docling_core_version = "1.1.0"
    docling_ibm_models_version = "1.2.0"
    docling_parse_version = "1.3.0"
    platform_str = "linux-x86_64"
    py_impl_version = "cpython"
    py_lang_version = "3.12"


class FakeInput:
    format = "pdf"
    file = "/tmp/sample.pdf"
    filesize = 12345
    page_count = 2
    document_hash = "abc123"


class FakeDocument:
    language = "ko"


class FakeResult:
    status = FakeStatus()
    timestamp = "2026-03-26T10:00:00"
    input = FakeInput()
    version = FakeVersion()
    document = FakeDocument()
    pages = [
        {"page_no": 1},
        {"page_no": 2},
    ]
    errors = [
        {"component_type": "OCR", "error_message": "minor warning"}
    ]
    timings = {
        "parse": {"count": 1, "duration": 0.5}
    }
    confidence = {"score": 0.95}
    assembled = {"body": True}


@pytest.fixture
def mock_dependencies(monkeypatch):
    from document_ai.parsers import docling_parser

    monkeypatch.setattr(docling_parser, "get_hf_tokenizer", lambda: FakeTokenizer())
    monkeypatch.setattr(
        docling_parser,
        "get_hybrid_hf_chunker",
        lambda serializer_provider=None: FakeChunker(),
    )
    monkeypatch.setattr(
        docling_parser,
        "serialize_meta",
        lambda meta: meta,
    )


def test_parse_docling_document_returns_parse_result(mock_dependencies):
    result = FakeResult()

    dto = _parse_docling_document(
        result=result,
        file_path="/tmp/sample.pdf",
        parser_mode="convert",
    )

    assert isinstance(dto, ParseResult)
    assert dto.parser_mode == "convert"
    assert dto.file_path == "/tmp/sample.pdf"
    assert dto.file_ext == ".pdf"

    assert dto.status == "SUCCESS"
    assert dto.timestamp == "2026-03-26T10:00:00"

    assert dto.input_format == "pdf"
    assert dto.input_file == "/tmp/sample.pdf"
    assert dto.input_filesize == 12345
    assert dto.input_page_count == 2
    assert dto.input_document_hash == "abc123"

    assert dto.parser_version == "1.0.0"
    assert dto.docling_core_version == "1.1.0"
    assert dto.docling_ibm_models_version == "1.2.0"
    assert dto.docling_parse_version == "1.3.0"
    assert dto.platform_str == "linux-x86_64"
    assert dto.py_impl_version == "cpython"
    assert dto.py_lang_version == "3.12"

    assert dto.detected_language == "ko"
    assert dto.page_count == 2
    assert dto.pages == [{"page_no": 1}, {"page_no": 2}]
    assert dto.errors == [{"component_type": "OCR", "error_message": "minor warning"}]
    assert dto.timings == {"parse": {"count": 1, "duration": 0.5}}
    assert dto.confidence == {"score": 0.95}
    assert dto.assembled == {"body": True}

    assert len(dto.chunks) == 2

    assert dto.chunks[0].chunk_index == 0
    assert dto.chunks[0].serialized_text == "This is intro chunk"
    assert dto.chunks[0].tokens == 4
    assert dto.chunks[0].meta == {"section": "intro"}

    assert dto.chunks[1].chunk_index == 1
    assert dto.chunks[1].serialized_text == "This is body chunk"
    assert dto.chunks[1].tokens == 4
    assert dto.chunks[1].meta == {"section": "body"}

def test_parse_docling_document_dump_json(mock_dependencies):
    result = FakeResult()

    dto = _parse_docling_document(
        result=result,
        file_path="/tmp/sample.pdf",
        parser_mode="convert",
    )

    dumped = dto.model_dump()

    assert isinstance(dumped, dict)
    assert "chunks" in dumped
    assert "status" in dumped
    assert "version_info" in dumped
    assert dumped["file_ext"] == ".pdf"

    dumped_json = dto.model_dump_json(indent=2)
    assert isinstance(dumped_json, str)
    assert '"parser_mode": "convert"' in dumped_json

def test_parse_docling_document_missing_fields(mock_dependencies):
    # Test when various optional fields are missing from the result
    class EmptyResult:
        status = None
        timestamp = None
        input = None
        version = None
        document = None
        pages = None
        errors = None
        timings = None
        confidence = None
        assembled = None

    dto = _parse_docling_document(
        result=EmptyResult(),
        file_path="/tmp/empty.txt",
        parser_mode="test_empty",
    )

    assert dto.parser_mode == "test_empty"
    assert dto.file_path == "/tmp/empty.txt"
    assert dto.status is None
    assert dto.timestamp is None
    assert dto.input_info is None
    assert dto.input_format is None
    assert dto.version_info is None
    assert dto.detected_language is None
    assert dto.page_count is None
    assert dto.pages is None
    assert dto.errors is None
    assert dto.timings is None
    assert dto.confidence is None
    assert dto.assembled is None


def test_parse_document_string(mock_dependencies, monkeypatch):
    from document_ai.parsers import docling_parser

    # Mock convert_to_markdown to return a simple string
    monkeypatch.setattr(docling_parser, "convert_to_markdown", lambda f: "Markdown Content")

    class MockConverter:
        def convert_string(self, content, format, name):
            # simulate return ConversionResult
            result = FakeResult()
            result.input.format = "md"
            return result
            
    monkeypatch.setattr(docling_parser, "get_converter", lambda: MockConverter())

    dto = docling_parser.parse_document_string(file_path="/tmp/test.md")
    
    assert dto.parser_mode == "convert_string_md"
    assert dto.file_ext == ".md"
    assert dto.input_format == "md"


if __name__ == "__main__":
    # pytest.main([__file__, "-k", "test_parse_docling_document_returns_parse_result"])
    # pytest.main([__file__, "-k", "test_parse_docling_document_dump_json"])
    pytest.main([__file__])