import json
from pathlib import Path

from ikischema import infer


def main() -> None:
    json_path = Path("examples/sample_data.json")
    json_path.parent.mkdir(exist_ok=True)

    payload = [
        {"id": 1, "name": "Ada", "score": 10.5, "active": True},
        {"id": 2, "name": "Grace", "score": None, "active": False},
        {"id": 3, "name": "Linus", "score": 15.25, "active": True},
    ]
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Created sample JSON at {json_path}")
    schema = infer(json_path)

    print("\nInferred schema from the JSON file:")
    print(schema)

    print("\nColumn inspection:")
    for column in schema.columns:
        print(f"- {column.name}: dtype={column.dtype}, nullable={column.nullable}")


if __name__ == "__main__":
    main()
