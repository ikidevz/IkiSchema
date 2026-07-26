import pandas as pd

from ikischema import infer


def main() -> None:
    frame = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Ada", "Grace", "Linus"],
            "score": [10.5, 20.0, None],
            "active": [True, False, True],
        }
    )

    print("Input pandas DataFrame:")
    print(frame)

    schema = infer(frame)
    print("\nInferred schema:")
    print(schema)

    print("\nDetailed column view:")
    for column in schema.columns:
        print(f"- {column.name}: dtype={column.dtype}, nullable={column.nullable}")


if __name__ == "__main__":
    main()
