from ikischema import SchemaContract, infer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


schema = infer([{"order_id": 1, "customer_id": 10, "total": 9.99}])
contract = SchemaContract.from_schema(
    schema, strictness={"additions_are_breaking": True})
contract.save("orders_contract.json")

new_data = [{"order_id": 2, "customer_id": 11,
             "total": 12.5, "coupon_code": "SAVE10"}]
violations = SchemaContract.load("orders_contract.json").validate(new_data)
for violation in violations:
    print(violation)
