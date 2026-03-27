from converterrier.cli import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.port == 8000
    assert args.max_size == 2 * 1024 * 1024 * 1024


def test_parse_args_custom_port():
    args = parse_args(["--port", "3000"])
    assert args.port == 3000


def test_parse_args_custom_max_size():
    args = parse_args(["--max-size", "500"])
    assert args.max_size == 500 * 1024 * 1024
