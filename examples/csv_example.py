from ikischema import infer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


csv_path = Path("examples/sample_data.csv")
csv_path.parent.mkdir(exist_ok=True)
csv_path.write_text(
    "id,name,score\n1,Ada,10.5\n2,Grace,20.0\n", encoding="utf-8")

schema = infer(csv_path)
print(schema)
