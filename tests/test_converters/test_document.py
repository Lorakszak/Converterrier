import subprocess
import pytest

from converterrier.converters.document import DocumentConverter


@pytest.fixture
def converter():
    return DocumentConverter()


@pytest.fixture
def md_file(tmp_path):
    path = tmp_path / "test.md"
    path.write_text("# Hello\n\nThis is a **test** document.\n")
    return path


@pytest.fixture
def txt_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_text("Hello, this is plain text.\n")
    return path


def _pandoc_available():
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def test_category(converter):
    assert converter.category == "document"


def test_supported_formats_has_md(converter):
    formats = converter.get_supported_formats()
    assert "md" in formats
    assert "html" in formats["md"]


def test_settings_schema_is_empty(converter):
    schema = converter.get_settings_schema("md")
    assert schema == {}


@pytest.mark.skipif(not _pandoc_available(), reason="Pandoc not installed")
def test_convert_md_to_html(converter, md_file):
    output = converter.convert(md_file, "html", {})
    assert output.exists()
    assert output.suffix == ".html"
    content = output.read_text()
    assert "<h1" in content or "Hello" in content


@pytest.mark.skipif(not _pandoc_available(), reason="Pandoc not installed")
def test_convert_txt_to_html(converter, txt_file):
    output = converter.convert(txt_file, "html", {})
    assert output.exists()
    content = output.read_text()
    assert "Hello" in content


@pytest.mark.skipif(not _pandoc_available(), reason="Pandoc not installed")
def test_convert_md_to_docx(converter, md_file):
    output = converter.convert(md_file, "docx", {})
    assert output.exists()
    assert output.suffix == ".docx"
    assert output.stat().st_size > 0
