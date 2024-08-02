from blackbox_decoder.log import GeneralInfo, Detail, Rollup, FlightInfo, Log
from blackbox_decoder.parse import parse_log
from datetime import timedelta

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


def test_detail():
    """
    Test the Detail class
    """
    detail = Detail(data["Millisecond detail"][0])
    assert detail["recNumb"] == 3758637126
    assert detail["entryTimeMsecs"] == 12093
    assert detail["type"] == 0
    assert detail["tethReady"] == 0
    assert detail["tethActive"] == 1
    assert detail["tethGood"] == 0
    assert detail["tethOn"] == 0
    assert detail["battOn"] == 0
    assert detail["battKill"] == 1
    assert detail["battDrain"] == 1
    assert detail["tethCurrentX10"] == 51.1
    assert detail["tethVoltX10"] == 0
    assert detail["battVoltX10"] == 0
    assert detail["outVoltX10"] == 153.6
    assert detail["battOutKill"] == 1
    assert detail["filler"] == 0


def test_rollup():
    """
    Test the Rollup class
    """
    rollup = Rollup(data["Minute Rollup"][0])
    assert rollup["recNumb"] == 4325737
    assert rollup["entryTimeMsecs"] == 78125
    assert rollup["type"] == 0
    assert rollup["tethReady"] == 0
    assert rollup["tethReadyChanges"] == 0
    assert rollup["tethActive"] == 0
    assert rollup["tethActiveChanges"] == 0
    assert rollup["tethGood"] == 0
    assert rollup["tethGoodChanges"] == 0
    assert rollup["tethOn"] == 0
    assert rollup["tethOnChanges"] == 0
    assert rollup["battOn"] == 0
    assert rollup["battOnChanges"] == 63
    assert rollup["battDrain"] == 0
    assert rollup["battDrainChanges"] == 0
    assert rollup["battKill"] == 0
    assert rollup["battKillChanges"] == 0
    assert rollup["tethCurrentX10Avg"] == -13.1
    assert rollup["tethCurrentX10Peak"] == 0.3
    assert rollup["tethVoltX10Avg"] == 0
    assert rollup["tethVoltX10Peak"] == 163.8
    assert rollup["battVoltX10Avg"] == 0
    assert rollup["battVoltX10Peak"] == 374.3
    assert rollup["outVoltX10Avg"] == 0
    assert rollup["outVoltX10Peak"] == 401.6
    assert rollup["battOutKill"] == 0
    assert rollup["battOutKillChanges"] == 63
    assert rollup["filler"] == 255
    assert rollup["filler2"] == 63
    assert rollup["maxTemp"] == -1


def test_flight_info():
    """
    Test the FlightInfo class
    """
    flight_info = FlightInfo(data["Flight Events"][0])
    assert flight_info["begRecNumb"] == 0
    assert flight_info["numbSecActive"] == 0
    assert flight_info["numbSecShutdown"] == 0
    assert flight_info["numbSecTethOn"] == 0
    assert flight_info["numbSecBattOn"] == 0
    assert flight_info["numbTethOnChanges"] == 0
    assert flight_info["numbTethGdChanges"] == 0
    assert flight_info["numbTethRdyChanges"] == 0
    assert flight_info["numbTethActChanges"] == 0
    assert flight_info["numbBattOnChanges"] == 0
    assert flight_info["numbBattKillChanges"] == 0
    assert flight_info["numbBattDrainChanges"] == 0
    assert flight_info["filler"] == 0
    assert flight_info["filler2"] == 0
    assert flight_info["maxTemp"] == -999
    assert flight_info["minTemp"] == 999
    assert flight_info["data"] == "Startin"


def test_log():
    """
    Test the Log class
    """
    log = Log("tests/test.log")
    assert log.flight_time == timedelta(seconds=129)
