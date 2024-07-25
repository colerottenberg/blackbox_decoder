import argparse
from typing import Dict, List

from bitstring import BitArray, Bits, BitStream, pack

from blackbox_decoder.app import app
from blackbox_decoder.log import Log, FlightRecord
from blackbox_decoder.parse import parse_log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a log file")
    parser.add_argument("log", type=str, help="The log file to parse")

    args = parser.parse_args()
    log = Log(args.log)
    if log:
        log.write_csv()

    record = FlightRecord(log)
