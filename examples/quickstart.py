from pathlib import Path

from ikischema import SchemaContract, check, diff, infer


def main() -> None:
    records = [
        {"order_id": 1, "customer_id": 10, "total": 9.99, "status": "pending"},
        {"order_id": 2, "customer_id": None, "total": 12.5, "status": "shipped"},
    ]

    print("Sample records used for inference:")
    for record in records:
        print(record)

    schema = infer(records)
    print("\nInferred schema:")
    print(schema)

    contract_path = Path("orders_contract.json")
    contract = SchemaContract.from_schema(schema)
    contract.save(contract_path)
    print(f"\nContract saved to {contract_path}")

    new_records = [{"order_id": 3, "customer_id": 12,
                    "total": 15.0, "status": "packed"}]
    print("\nValidating a new batch of records:")
    violations = check(new_records, contract_path)
    if violations:
        for violation in violations:
            print(violation)
    else:
        print("No violations found.")

    schema_a = infer([{"id": 1, "name": "Ada"}])
    schema_b = infer([{"id": 1, "name": "Ada", "score": 10.5}])

    print("\nSchema diff summary:")
    print(diff(schema_a, schema_b).summary())


if __name__ == "__main__":
    main()
