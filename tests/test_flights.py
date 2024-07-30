from blackbox_decoder.log import FlightRecord
from datetime import timedelta

import pandas as pd

record = FlightRecord("tests/test.log")


def test_FlightRecord():
    """
    Test the FlightRecord class for the following attributes:
    - Lenght: the number of flights within the record
    - Flight Time: the total time of all flights in the record
    - Drone Name: the name of the drone
    - Chrono Order: the chronological order of timestamps in each flight
    """

    assert len(record) == 46
    assert record.get_flight_time() == timedelta(seconds=129)
    assert record.get_drone_name() == "BV-ALEDPM"

    # Check the chronological order of timestamps


def test_chrono_order():
    """
    For each of the 46 flights, turn them to a dataframe and check the "entryTimeMsecs" column for an ascending order
    """
    # Empty numpy array to store the entryTimeMsecs of each flight
    empty = pd.DataFrame()
    for i in range(len(record) - 1):
        flight = record.to_dataframe(i)
        entryTimeMsecs = flight["entryTimeMsecs"]
        assert (entryTimeMsecs == entryTimeMsecs.sort_values()).all()
