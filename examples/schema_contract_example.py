from pathlib import Path

from ikischema import SchemaContract, infer


def main() -> None:
    sample_records = [
        {"order_id": 1, "customer_id": 10, "total": 9.99, "status": "pending"},
        {"order_id": 2, "customer_id": 11, "total": 12.5, "status": "shipped"},
    ]

    schema = infer(sample_records)
    print("Original schema inferred from records:")
    print(schema)

    contract_path = Path("examples/generated_contract.json")
    contract = SchemaContract.from_schema(schema)
    contract.save(contract_path)
    print(f"\nSaved contract to {contract_path}")

    loaded = SchemaContract.load(contract_path)
    print("\nLoaded contract schema:")
    print(loaded.schema)

    compatible_data = [
        {"order_id": 3, "customer_id": 12, "total": 15.0, "status": "packed"},
    ]
    incompatible_data = [
        {"order_id": 4, "customer_id": 13, "total": 18.75,
            "status": "delivered", "coupon_code": "SAVE10"},
    ]

    print("\nValidating a compatible batch:")
    compatible_violations = loaded.validate(compatible_data)
    if compatible_violations:
        for violation in compatible_violations:
            print(violation)
    else:
        print("No violations found.")

    print("\nValidating a batch with an unexpected column:")
    incompatible_violations = loaded.validate(incompatible_data)
    if incompatible_violations:
        for violation in incompatible_violations:
            print(violation)
    else:
        print("No violations found.")


if __name__ == "__main__":
    main()
