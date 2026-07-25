from ikischema import infer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


json_path = Path("examples/sample_data.json")
json_path.parent.mkdir(exist_ok=True)
json_path.write_text(
    '[{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]', encoding="utf-8")

schema = infer(json_path)
print(schema)
