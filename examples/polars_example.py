from ikischema import infer
import polars as pl
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


frame = pl.DataFrame(
    {"id": [1, 2], "name": ["Ada", "Grace"], "score": [10.5, 20.0]})
schema = infer(frame)
print(schema)
