from ikischema import SchemaContract, infer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


schema = infer([{"order_id": 1, "customer_id": 10, "total": 9.99}])
contract = SchemaContract.from_schema(schema)
contract.save("examples/generated_contract.json")
loaded = SchemaContract.load("examples/generated_contract.json")
print(loaded.schema)
