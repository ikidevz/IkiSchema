from ikischema import SchemaContract, check, diff, infer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


records = [
    {"order_id": 1, "customer_id": 10, "total": 9.99},
    {"order_id": 2, "customer_id": None, "total": 12.5},
]

schema = infer(records)
print(schema)

contract = SchemaContract.from_schema(schema)
contract.save("orders_contract.json")

new_records = [{"order_id": 3, "customer_id": 12, "total": 15.0}]
violations = check(new_records, "orders_contract.json")
print(violations)

schema_a = infer([{"id": 1, "name": "Ada"}])
schema_b = infer([{"id": 1, "name": "Ada", "score": 10.5}])
print(diff(schema_a, schema_b).summary())
