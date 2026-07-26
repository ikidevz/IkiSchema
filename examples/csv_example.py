from pathlib import Path

from ikischema import infer


def main() -> None:
    csv_path = Path("examples/sample_data.csv")
    csv_path.parent.mkdir(exist_ok=True)
    csv_path.write_text(
        "id,name,score,active\n"
        "1,Ada,10.5,true\n"
        "2,Grace,20.0,false\n"
        "3,Linus,15.25,true\n",
        encoding="utf-8",
    )

    print(f"Created sample CSV at {csv_path}")
    schema = infer(csv_path)

    print("\nInferred schema from the CSV file:")
    print(schema)

    print("\nColumn summary:")
    for column in schema.columns:
        print(
            f"- {column.name}: dtype={column.dtype}, nullable={column.nullable}"
        )


if __name__ == "__main__":
    main()
