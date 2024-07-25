import argparse
from typing import Dict, List

from bitstring import BitArray, Bits, BitStream, pack
import matplotlib.pyplot as plt

from app import app
from log import Detail, FlightInfo, GeneralInfo, Log, Rollup, FlightRecord
from parse import parse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a log file")
    parser.add_argument("log", type=str, help="The log file to parse")

    args = parser.parse_args()
    log = Log(args.log)
    if log:
        log.write_csv()

    record = FlightRecord(log)

    df = record.to_dataframe()
    df.set_index("recNumb", inplace=True)

    df.to_csv("data.csv")
    plt.step(df.index, df["tethGood"], where="post", color="blue")
    plt.step(df.index, df["tethReady"], where="post", color="red")
    plt.step(df.index, df["tethOn"], where="post", color="green")
    plt.xlabel("Time")
    plt.ylabel("Tether Status")
    plt.legend(["tethGood", "tethReady", "tethOn"])
    plt.show()
    # app.run(debug=True)
