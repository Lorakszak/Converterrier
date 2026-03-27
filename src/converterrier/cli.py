import argparse
import webbrowser

import uvicorn

from converterrier.app import create_app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="converterrier",
        description="Local file format converter",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=2048,
        help="Max upload size in MB (default: 2048)",
    )
    args = parser.parse_args(argv)
    args.max_size = args.max_size * 1024 * 1024
    return args


def main():
    args = parse_args()
    app = create_app(max_size=args.max_size)

    url = f"http://localhost:{args.port}"
    print(f"Starting Converterrier at {url}")
    webbrowser.open(url)

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
