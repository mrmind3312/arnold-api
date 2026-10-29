from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from arnold_api import ArnoldAPI

app = ArnoldAPI()
app.load(Path(__file__).with_name("hello.arnoldc"))
app.serve(host="127.0.0.1", port=8080)
