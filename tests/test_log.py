import pytest
from blackbox_decoder.log import GeneralInfo, Detail, Rollup, FlightInfo, Log
from blackbox_decoder.parse import parse_log

data = parse_log("tests/test.log")


def test_general_info():
    """
    Test the GeneralInfo class
    """
    gen_info = GeneralInfo(data["General Info"][0])

    assert gen_info["ID"] == "BV-ALEDPM"
    assert gen_info["version"] == 1
    assert gen_info["powerups"] == 106
    assert gen_info["mins_run"] == 0


# def test_detail():
#     """
#     Test the Detail class
#     """
#     data: str = "000   0x0020  2c000000 003ff880 000179ef 00420235 "

#     detail = Detail(data)

# def test_rollup():
#     """
#     Test the Rollup class
#     """

# def test_flight_info():
#     """
#     Test the FlightInfo class
#     """

# def test_log():
#     """
#     Test the Log class
#     """

