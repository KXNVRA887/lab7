"""Запуск всех частей работы с сохранением протоколов."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")
for script, output in (("main.py", "output_main.txt"),
                       ("experiments.py", "output_experiments.txt"),
                       ("exercises.py", "output_exercises.txt")):
    result = subprocess.run(
        [sys.executable, "-B", script], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    text = result.stdout + result.stderr
    (ROOT / output).write_text(text, encoding="utf-8")
    print(f"=== {script} -> {output} ===", text, sep="\n", flush=True)
    if result.returncode:
        sys.exit(result.returncode)
