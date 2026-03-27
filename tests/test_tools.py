from converterrier.tools import check_tools, ToolStatus


def test_check_tools_returns_tool_status():
    result = check_tools()
    assert isinstance(result, ToolStatus)
    assert isinstance(result.ffmpeg, bool)
    assert isinstance(result.pandoc, bool)
    assert isinstance(result.pandoc_pdf, bool)
