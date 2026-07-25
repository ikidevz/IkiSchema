from ikischema import diff, infer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


left = infer([{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}])
right = infer([{"id": 1, "name": "Ada", "score": 10.5}, {
              "id": 2, "name": "Grace", "score": 20.0}])

result = diff(left, right)
print(result.summary())
for violation in result.type_changes:
    print(violation)
