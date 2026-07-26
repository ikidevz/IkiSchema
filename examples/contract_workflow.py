from pathlib import Path

from ikischema import SchemaContract, infer


def main() -> None:
    contract_path = Path("orders_contract.json")

    sample_records = [
        {"order_id": 1, "customer_id": 10, "total": 9.99, "status": "pending"},
        {"order_id": 2, "customer_id": 11, "total": 12.5, "status": "shipped"},
    ]

    print("Inspecting a sample batch of orders...")
    for record in sample_records:
        print(record)

    schema = infer(sample_records)
    print("\nInferred schema:")
    print(schema)

    contract = SchemaContract.from_schema(
        schema,
        strictness={"additions_are_breaking": True},
    )
    contract.save(contract_path)
    print(f"\nSaved contract to {contract_path}")

    loaded_contract = SchemaContract.load(contract_path)

    compatible_data = [
        {"order_id": 3, "customer_id": 12, "total": 15.0, "status": "packed"},
    ]
    incompatible_data = [
        {
            "order_id": 4,
            "customer_id": 13,
            "total": 18.75,
            "status": "delivered",
            "coupon_code": "SAVE10",
        }
    ]

    print("\nValidating a compatible batch:")
    compatible_violations = loaded_contract.validate(compatible_data)
    if compatible_violations:
        for violation in compatible_violations:
            print(violation)
    else:
        print("No violations found.")

    print("\nValidating a batch that introduces a new column:")
    incompatible_violations = loaded_contract.validate(incompatible_data)
    if incompatible_violations:
        for violation in incompatible_violations:
            print(violation)
    else:
        print("No violations found.")


if __name__ == "__main__":
    main()
