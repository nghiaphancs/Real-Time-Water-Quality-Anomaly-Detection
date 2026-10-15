import os
import pytest
from edge.settings import get_project_root
from edge.sources.csv_source import CsvSource


def test_csv_source_sequential():
    root = get_project_root()
    dataset_dir = os.path.join(root, "data", "datasets")
    mapping_dir = os.path.join(root, "configs", "mappings")

    source = CsvSource(
        dataset_dir=dataset_dir,
        mapping_dir=mapping_dir,
        csv_file="china_water_pollution_data.csv",
        order="sequential",
        loop=True,
        interval_sec=0.0, # zero interval for instant testing
    )
    source.start()

    r1 = source.poll_reading()
    assert r1 is not None
    assert r1.seq == 1
    assert "pH" in r1.values
    assert "DO" in r1.values

    r2 = source.poll_reading()
    assert r2 is not None
    assert r2.seq == 2
