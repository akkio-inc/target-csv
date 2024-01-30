"""Tests standard target features using the built-in SDK tests library."""
from pathlib import Path
from typing import Any, Dict

import os
from singer_sdk.testing import get_standard_target_tests, TargetTestRunner

from target_csv.target import TargetCSV

SAMPLE_CONFIG: Dict[str, Any] = {
    "output_path_prefix": ".output/"
}

# Run standard built-in target tests from the SDK:
def test_standard_target_tests():
    """Run standard target tests from the SDK."""

    filepath = os.path.join(".output", "input_stream.csv")
    Path(filepath).unlink(missing_ok=True)

    runner = TargetTestRunner(
        target_class=TargetCSV,
        config=SAMPLE_CONFIG,
        input_filepath=Path("./target_csv/tests/data.jsonl")
    )
    runner.sync_all()

    # assert output looks as anticipated
    with open(filepath) as f:
        text = f.read()
        assert "id,predicted_value" in text
        assert "5922,0.8" in text
        assert "461,0.3" in text