"""
Unit tests for data validation logic.
Verifies that validation functions correctly pass valid datasets and flag injected corruptions.
"""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/data"))
from validate_telemetry import validate_telemetry_dataset

def test_telemetry_validation_on_clean_data():
    """Verify clean generated dataset passes all 14 validation checks."""
    success, errors = validate_telemetry_dataset()
    assert success is True
    assert len(errors) == 0

def test_telemetry_validation_catches_negative_values(tmp_path):
    """Verify validator flags negative consumption values."""
    clean_csv = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
    df = pd.read_csv(clean_csv).head(50)
    # Corrupt a value to negative
    df.loc[5, "hourly_consumption_liters"] = -15.0
    bad_csv = tmp_path / "corrupt_data.csv"
    df.to_csv(bad_csv, index=False)

    success, errors = validate_telemetry_dataset(data_path=str(bad_csv))
    assert success is False
    assert any("negative consumption" in e for e in errors)
