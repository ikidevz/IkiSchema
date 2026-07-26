from ikischema import diff, infer


def main() -> None:
    left = infer(
        [
            {"id": 1, "name": "Ada"},
            {"id": 2, "name": "Grace"},
        ]
    )
    right = infer(
        [
            {"id": 1, "name": "Ada", "score": 10.5},
            {"id": 2, "name": "Grace", "score": 20.0},
        ]
    )

    print("Schema A:")
    print(left)

    print("\nSchema B:")
    print(right)

    result = diff(left, right)
    print("\nDiff summary:")
    print(result.summary())

    print("\nType changes detected:")
    for violation in result.type_changes:
        print(violation)

    print("\nNullability changes detected:")
    for violation in result.nullability_changes:
        print(violation)


if __name__ == "__main__":
    main()
