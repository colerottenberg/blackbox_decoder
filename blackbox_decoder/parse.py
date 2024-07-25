import datetime
import re

HEADER = [
    "General Info",
    "Millisecond detail",
    "Minute Rollup",
    "Second Rollup",
    "Flight Events",
]
TIMESTAMP = [
    "[BEGIN]",
    "[END]",
]  # Timestamps to look for at the beginning of a line containing a timestamp
FORMAT = "%m/%d/%Y %H:%M:%S %p"  # Format of the timestamps
PATTERNS = {
    "General Info": re.compile(
        r"^(\d{3})\s+(0x[0-9a-fA-F]{4})\s+([0-9a-fA-F]{2})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})$"
    ),  # General Info: 25 bytes
    "Millisecond detail": re.compile(
        r"^(\d{3})\s+(0x[0-9a-fA-F]{4})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})$"
    ),  # Millisecond detail: 16 bytes
    "Minute Rollup": re.compile(
        r"^(\d{3})\s+(0x[0-9a-fA-F]{4})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})$"
    ),  # Minute Rollup: 32 bytes
    "Second Rollup": re.compile(
        r"^(\d{3})\s+(0x[0-9a-fA-F]{4})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})$"
    ),  # Second Rollup: 32 bytes
    "Flight Events": re.compile(
        r"^(\d{3})\s+(0x[0-9a-fA-F]{4})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})$"
    ),  # Flight Events: 40 bytes
}


def parse_log(log: str) -> dict:
    data = {
        "General Info": [],
        "Millisecond detail": [],
        "Minute Rollup": [],
        "Second Rollup": [],
        "Flight Events": [],
        "Flight Time": datetime.timedelta(0),
    }
    beginning: datetime.datetime
    end: datetime.datetime
    with open(log, "r", encoding="utf-16-le") as file:
        # First Read the file to find the beginning timestamp
        """
        1. Read the file line by line:
        2. Check for the first timestamp and store the timestamp that follows
        3. For each header in the HEADER list, read until the header is found
        3.1 Skip the format desc line and read the data until the the REGEX pattern is found
        3.2 Store the data in a list
        4. Repeat the process for each header
        """

        # 1.
        for line in file:
            if TIMESTAMP[0] in line:
                # Strip the TIMESTAMP[0] from the line
                line = line.replace(TIMESTAMP[0], "").strip("\ufeff").strip()
                beginning = datetime.datetime.strptime(line, "%m/%d/%Y %H:%M:%S %p")
                break

        for line in file:
            for header in HEADER:
                if header in line:
                    # Skip the format desc line
                    next(file)
                    # Read the data until the next header is found
                    for line in file:
                        if TIMESTAMP[1] in line:
                            # Strip the TIMESTAMP[1] from the line
                            line = (
                                line.replace(TIMESTAMP[1], "").strip("\ufeff").strip()
                            )
                            end = datetime.datetime.strptime(
                                line, "%m/%d/%Y %H:%M:%S %p"
                            )
                            break
                        # Check if the line matches the pattern
                        if PATTERNS[header].match(line.strip()):
                            data[header].append(line.strip())
                        else:
                            break
        if TIMESTAMP[1] in line:
            # Strip the TIMESTAMP[1] from the line
            line = line.replace(TIMESTAMP[1], "").strip("\ufeff").strip()
            end = datetime.datetime.strptime(line, "%m/%d/%Y %H:%M:%S %p")

        data["Flight Time"] = end - beginning

        return data
