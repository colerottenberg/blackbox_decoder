import csv
import datetime
from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd

from bitstring import BitStream

from blackbox_decoder.parse import parse_log

SIGMA = 8

LOG_PACKET_SIZES = {
    "GeneralInfo": 25,
    "Detail": 16,
    "Rollup": 32,
    "FlightInfo": 40,
}


class BaseLog:
    def __init__(self, data: str):
        parts = data.split()
        self.rec = int(parts[0])
        self.offset = int(parts[1], 16)
        self.concat = "".join(parts[2:])
        self.s = BitStream(hex=self.concat)
        self.structure = {}

    def __str__(self):
        s = ""
        for key, value in self.structure.items():
            s += f"{key}: {value}\n"

        return s

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.structure.values())

    def __getitem__(self, key):
        return self.structure[key]

    def packet_size(self):
        return LOG_PACKET_SIZES[self.__class__.__name__]

    def get_size_struct(self) -> Dict[str, Tuple[str, int]]:
        """
        This method should be implemented in the subclass and should return a dictionary
        where the key is the name of the field and the value is a tuple where the first
        """
        raise NotImplementedError("This method must be implemented in the subclass")


class GeneralInfo(BaseLog):
    """
    The GeneralInfo class is a subclass of the BaseLog class and is used to parse the General Info packet

    The General Info packet contains the following fields:
    - ID: A 10 byte identifier
    - version: The version of the log structures
    - date_initialized: The date these structures were created in epoch time
    - last_rec_number: The record number that last time we started
    - powerups: The number of powerups
    - mins_run: The number of minutes the log has been running
    """

    def __init__(self, data: str):
        super().__init__(data)
        size_struct = self.get_size_struct()

        bit_sum = sum(value[1] for value in size_struct.values())
        shift = (8 * self.packet_size()) % bit_sum

        self.s.pos = shift

        for key, value in size_struct.items():
            self.structure[key] = self.s.read(value[0])

        self.structure["ID"] = (
            self.structure["ID"].decode()[::-1].translate({ord("\x00"): None})
        )
        self.structure["date_initialized"] = datetime.datetime.fromtimestamp(
            self.structure["date_initialized"]
        )
        self.structure = dict(reversed(list(self.structure.items())))
        assert self.s.pos == self.s.len

    def get_size_struct(self) -> Dict[str, Tuple[str, int]]:
        """
        The size and structure of the General Info packet

        This method returns a dictionary where the key is the name of the field and the value is a tuple
        The tuple contains: the type of the field and the size of the field in bits

        Args:
            None

        Returns:
            Dict[str, (str, int)]: A dictionary where the key is the name of the field and the value is a tuple
        """
        return {
            "mins_run": ("uint:32", 32),
            "powerups": ("uint:16", 16),
            "last_rec_number": ("uint:32", 32),
            "date_initialized": ("uint:32", 32),
            "version": ("uint:8", 8),
            "ID": ("bytes:10", 10 * 8),
        }


class Detail(BaseLog):
    """
    The Detail class is a subclass of the BaseLog class and is used to parse the Detail packet

    The Detail packet appears in our logs in millisecond detail and contains the following fields:
    - recNumb: An upward counting record counter to find end on powerup
    - entryTimeMsecs: The millisecond of run time when this entry was created.
    - type: The type of record (0 - detail data, others reserved)
    - tethReady: 1 bit each for the main flags
    - tethActive: 1 bit each for the main flags
    - tethGood: 1 bit each for the main flags
    - tethOn: 1 bit each for the main flags
    - battOn: 1 bit each for the main flags
    - battKill: 1 bit each for the main flags
    - battDrain: 1 bit each for the main flags
    - tethCurrentX10: These values are all stored as 11 bits
    - tethVoltX10: These values are all stored as 11 bits
    - battVoltX10: These values are all stored as 11 bits
    - outVoltX10: These values are all stored as 11 bits
    - chgAcok: 1 bit each for the main flags
    - chgState: 1 bit each for the main flags
    - lowPower: 1 bit each for the main flags
    """

    def __init__(self, data: str):
        super().__init__(data)
        # This is a store of both the size and the structure of the data
        size_struct = self.get_size_struct()
        # Reverse the size_struct dictionary for the BitStream
        size_struct = dict(reversed(list(size_struct.items())))
        # We calculate the total number of bits in the structure and shift the bits to align the data we parse
        bit_sum = sum(value[1] for value in size_struct.values())
        shift = (
            8 * LOG_PACKET_SIZES["Detail"]
        ) % bit_sum  # WE SHIFT THE BITS TO ALIGN THE DATA
        self.s.pos = shift
        # WE parse the data using the accepted type and size using the size_struct
        for key, value in size_struct.items():
            self.structure[key] = self.s.read(value[0])

        # Reverse the structure to its original structure in the C code
        self.structure = dict(reversed(list(self.structure.items())))

    def get_size_struct(self) -> Dict[str, Tuple[str, int]]:
        """
        The size and structure of the General Info packet

        This method returns a dictionary where the key is the name of the field and the value is a tuple
        The tuple contains: the type of the field and the size of the field in bits

        Args:
            None

        Returns:
            Dict[str, (str, int)]: A dictionary where the key is the name of the field and the value is a tuple
        """
        return {
            "lowPower": ("uint:1", 1),
            "chgState": ("uint:1", 1),
            "chgAcok": ("uint:1", 1),
            "outVoltX10": ("uint:12", 12),
            "battVoltX10": ("uint:12", 12),
            "tethVoltX10": ("uint:12", 12),
            "tethCurrentX10": ("int:12", 12),
            "battDrain": ("uint:1", 1),
            "battKill": ("uint:1", 1),
            "battOn": ("uint:1", 1),
            "tethOn": ("uint:1", 1),
            "tethGood": ("uint:1", 1),
            "tethActive": ("uint:1", 1),
            "tethReady": ("uint:1", 1),
            "type": ("uint:3", 3),
            "entryTimeMsecs": ("uint:32", 32),
            "recNumb": ("uint:32", 32),
        }


class Rollup(BaseLog):
    def __init__(self, data: str):
        super().__init__(data)
        size_struct = self.get_size_struct()
        # Reverse the size_struct dictionary for the BitStream
        size_struct = dict(reversed(list(size_struct.items())))

        bit_sum = sum(value[1] for value in size_struct.values())
        shift = (8 * LOG_PACKET_SIZES["Rollup"]) % bit_sum
        self.s.pos = shift

        for key, value in size_struct.items():
            self.structure[key] = self.s.read(value[0])

        # Reverse the structure to its original structure in the C code
        self.structure = dict(reversed(list(self.structure.items())))
        assert self.s.pos == self.s.len

    def get_size_struct(self) -> Dict[str, Tuple[str, int]]:
        """
        The size and structure of the General Info packet

        This method returns a dictionary where the key is the name of the field and the value is a tuple
        The tuple contains: the type of the field and the size of the field in bits

        Args:
            None

        Returns:
            Dict[str, (str, int)]: A dictionary where the key is the name of the field and the value is a tuple
        """
        return {
            "recNumb": ("uint:32", 32),
            "entryTimeMsecs": ("uint:32", 32),
            "type": ("uint:4", 4),
            "tethReady": ("uint:1", 1),
            "tethReadyChanges": ("uint:6", 6),
            "tethActive": ("uint:1", 1),
            "tethActiveChanges": ("uint:6", 6),
            "tethGood": ("uint:1", 1),
            "tethGoodChanges": ("uint:6", 6),
            "tethOn": ("uint:1", 1),
            "tethOnChanges": ("uint:6", 6),
            "battOn": ("uint:1", 1),
            "battOnChanges": ("uint:6", 6),
            "battDrain": ("uint:1", 1),
            "battDrainChanges": ("uint:6", 6),
            "battKill": ("uint:1", 1),
            "battKillChanges": ("uint:6", 6),
            "tethCurrentX10Avg": ("int:12", 12),
            "tethCurrentX10Peak": ("int:12", 12),
            "tethVoltX10Avg": ("uint:12", 12),
            "tethVoltX10Peak": ("uint:12", 12),
            "battVoltX10Avg": ("uint:12", 12),
            "battVoltX10Peak": ("uint:12", 12),
            "outVoltX10Avg": ("uint:12", 12),
            "outVoltX10Peak": ("uint:12", 12),
            "chgAcok": ("uint:1", 1),
            "chgAcokChanges": ("uint:6", 6),
            "chgStatus": ("uint:1", 1),
            "chgStatusChanges": ("uint:6", 6),
            "lowPower": ("uint:1", 1),
            "lowPowerChanges": ("uint:6", 6),
            "maxTemp": ("int:8", 8),
            "filler3": ("int:8", 8),
        }


class FlightInfo(BaseLog):
    """
    The FlightInfo class is a subclass of the BaseLog class and is used to parse the Flight Info packet

    The Flight Info packet contains the following fields:
    - data: A 7 byte identifier
    - minTemp: The minimum temperature
    - maxTemp: The maximum temperature
    - numbLowPwrChanges: The number of low power changes
    - numbChgAcokChanges: The number of charge acok changes
    - numbChgStatChanges: The number of charge status changes
    - numbBattDrainChanges: The number of battery drain changes
    - numbBattKillChanges: The number of battery kill changes
    - numbBattOnChanges: The number of battery on changes
    - numbTethActChanges: The number of tether active changes
    - numbTethRdyChanges: The number of tether ready changes
    - numbTethGdChanges: The number of tether good changes
    - numbTethOnChanges: The number of tether on changes
    - numbSecBattOn: The number of seconds the battery was on
    - numbSecTethOn: The number of seconds the tether was on
    - numbSecShutdown: The number of seconds the unit was shutdown
    - numbSecActive: The number of seconds the unit was active
    - begRecNumb: The record number that last time we started
    """

    def __init__(self, data: str):
        super().__init__(data)
        size_struct = self.get_size_struct()
        # Reverse the size_struct dictionary for the BitStream
        size_struct = dict(reversed(list(size_struct.items())))

        bit_sum = sum(value[1] for value in size_struct.values())
        shift = (8 * LOG_PACKET_SIZES[self.__class__.__name__]) % bit_sum
        self.s.pos = shift

        for key, value in size_struct.items():
            self.structure[key] = self.s.read(value[0])

        try:
            self.structure["data"] = self.structure["data"].decode("utf-8")[::-1]
        except UnicodeDecodeError:
            self.structure["data"] = "ERROR"
        # Reverse the structure to its original structure in the C code
        self.structure = dict(reversed(list(self.structure.items())))
        assert self.s.pos == self.s.len

    def get_size_struct(self) -> Dict[str, Tuple[str, int]]:
        """
        The size and structure of the General Info packet

        This method returns a dictionary where the key is the name of the field and the value is a tuple
        The tuple contains: the type of the field and the size of the field in bits

        Args:
            None

        Returns:
            Dict[str, (str, int)]: A dictionary where the key is the name of the field and the value is a tuple
        """
        return {
            "begRecNumb": ("uint:32", 32),
            "numbSecActive": ("uint:32", 32),
            "numbSecShutdown": ("uint:32", 32),
            "numbSecTethOn": ("uint:32", 32),
            "numbSecBattOn": ("uint:32", 32),
            "numbTethOnChanges": ("uint:8", 8),
            "numbTethGdChanges": ("uint:8", 8),
            "numbTethRdyChanges": ("uint:8", 8),
            "numbTethActChanges": ("uint:8", 8),
            "numbBattOnChanges": ("uint:8", 8),
            "numbBattKillChanges": ("uint:8", 8),
            "numbBattDrainChanges": ("uint:8", 8),
            "numbChgStatChanges": ("uint:8", 8),
            "numbChgAcokChanges": ("uint:8", 8),
            "numbLowPwrChanges": ("uint:8", 8),
            "minTemp": ("int:12", 12),
            "maxTemp": ("int:12", 12),
            "data": ("bytes:7", 7 * 8),
        }


class Log:
    def __init__(self, log_file: str):
        self.data = parse_log(log_file)
        self.flight_time = self.data["Flight Time"]
        self.gen_info = GeneralInfo(self.data["General Info"][0])
        self.milli_detail = [Detail(x) for x in self.data["Millisecond detail"]]
        self.minute_rollup = [Rollup(x) for x in self.data["Minute Rollup"]]
        self.second_rollup = [Rollup(x) for x in self.data["Second Rollup"]]
        self.flight_events = [FlightInfo(x) for x in self.data["Flight Events"]]
        # Writing the data to a CSV file

    def write_csv(self):
        # Gen Info to CSV
        with open("GenInfo.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.gen_info.structure.keys())
            writer.writerow(self.gen_info.structure.values())

        # Detail to CSV
        with open("Detail.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.milli_detail[0].structure.keys())
            for detail in self.milli_detail:
                writer.writerow(detail.structure.values())

        # Rollup to CSV
        with open("MinuteRollup.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.minute_rollup[0].structure.keys())
            for rollup in self.minute_rollup:
                writer.writerow(rollup.structure.values())

        with open("SecondRollup.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.second_rollup[0].structure.keys())
            for rollup in self.second_rollup:
                writer.writerow(rollup.structure.values())

        # Flight Info to CSV
        with open("FlightInfo.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.flight_events[0].structure.keys())
            for flight_info in self.flight_events:
                writer.writerow(flight_info.structure.values())

    def __bool__(self):
        # If the size of the data is 0, return False
        return bool(self.data)


class FlightRecord:
    """
     The FlightRecord class is used to store the flight records of the drone

     In its current implementation, a log file can contain the records of multiple flights. In order to accurately splice the records of each flight, we need to know when each flight starts and ends. This is where the FlightRecord class comes in.

    The Details log updates every millisecond and the Rollup log updates every second AND every minute. The FlightInfo log updates per flight. We need to be able to first split the minute rollup if there are multiple flights in the log. If there are multiple flights in the log, we need to split the minute rollup logs into two flights. Using the corresponding recNumbs in the minute rollup logs, we can determine the start and end of each flight. We can then splice together the second and minute rollup logs for each flight.
    """

    def __init__(self, input: Union[str, Log]):
        """
        The constructor for the FlightRecord class

        Args:
            input (Union[str, Log]): The input can either be a string or a Log object

        Returns:
            None
        """
        if isinstance(input, str):
            self.log = Log(input)
        else:
            self.log = input

        minute_flights: List[List[Rollup]] = self.split_flights(self.log.minute_rollup)

        second_flights: List[List[Rollup]] = self.split_flights(self.log.second_rollup)

        self.flights: List[Log] = self.combining_logs(
            minute_flights=self.log.minute_rollup, second_flights=self.log.second_rollup
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        This method converts the flight records into a pandas DataFrame
        The index of the DataFrame is the recNumb field in the data dictionary

        Args:
            None

        Returns:
            pd.DataFrame: A pandas DataFrame containing the flight records
        """
        df: pd.DataFrame = pd.DataFrame([flight.structure for flight in self.flights])
        return df

    def combining_logs(
        self, minute_flights: List[Rollup], second_flights: List[Rollup]
    ) -> List[Log]:
        """
        This method combines the second and minute rollup logs for each flight allowing for better analysis

        Args:
            minute_flights (List[List[Rollup]]): A list of minute rollup logs for each flight
            second_flights (List[List[Rollup]]): A list of second rollup logs for each flight

        Returns:
            List[List[Log]]: A list of Log objects where each object contains the data for each fligh
        """

        # Based on the mean of each minute rollup log, we can determine which second rollup logs belong to each flight

        # We can then splice together the second and minute rollup logs for each flight

        # @TODO: Fix the decoding of the minute rollup logs and actually combine the logs

        combined_flights: List[Log] = []
        combined_flights = second_flights
        combined_flights.sort(key=lambda x: x.structure["recNumb"])
        return combined_flights

    def split_flights(self, rollup_log: List[Rollup]) -> List[List[Rollup]]:
        """
        This method splits the log into multiple flights

        This method splits the log into multiple flights. The minute rollup logs are used to determine the start and end of each flight. The method returns a list of Log objects where each object contains the data for each flight.

        Args:
            None

        Returns:
            List[Log]: A list of Log objects where each object contains the data for each flight
        """
        # We first need to determine the start and end of each flight using the minute rollup logs
        # We can then splice together the second and minute rollup logs for each flight
        # We can then return a list of Log objects where each object contains the data for each flight

        # We need to combine the second and minute rollup logs for each flight
        rollups: List[Rollup] = rollup_log

        # We first need to sort the list based on the recNumb
        rollups.sort(key=lambda x: x.structure["recNumb"])

        differences = np.diff([x.structure["recNumb"] for x in rollups])

        mean_diff = np.mean(differences)
        std_diff = np.std(differences)

        Threshold = mean_diff + SIGMA * std_diff

        # Using our 2 Sigma rule, if a difference is greater than 2 standard deviations from the mean, we can assume that it is the start of a new flight.
        # We will mark each difference greater than the threshold as the start of a new flight

        indices = []
        for i, diff in enumerate(differences):
            if diff > Threshold:
                indices.append(i)

        # We can now split the rollups into different flights
        flights: List[List[Rollup]] = []
        start = 0
        for index in indices:
            flights.append(rollups[start:index])
            start = index

        flights.append(rollups[start:])

        return flights
