import argparse
import json
import sys

from . import infer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ikischema")
    subparsers = parser.add_subparsers(dest="command", required=True)

    infer_parser = subparsers.add_parser("infer")
    infer_parser.add_argument("payload")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "infer":
        payload = json.loads(args.payload)
        schema = infer(payload)
        print(schema)
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
