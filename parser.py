#
#    This file is part of ESXi LSI RAID Monitoring.
#
#     ESXi LSI RAID Monitoring is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     ESXi LSI Raid Monitoring is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
#
# This is the parser module for the ESXi RAID Monitoring Script
#
# It checks the passed pd-, ld-, adapter- status string if it shows any failure indications
#

import logging

logger = logging.getLogger("parser")


def check_ld(ld_data):
    data = split_data_string(ld_data["data"])
    logger.info("Parsing Logical Disk Data")
    logger.debug("Got data for ld: {0}".format(data))
    errors = 0

    if "Virtual Drive" not in data:
        logger.critical("Virtual Drive not present in data")
        errors += 1
    else:
        errors += verify_value_and_presence("State",
                                  "Optimal",
                                  "Virtaul Drive {0}".format(data["Virtual Drive"]),
                                  data)

    return errors


def check_pd(pd_data):
    data = split_data_string(pd_data["data"])
    logger.info("Parsing Physical Disk Data")
    logger.debug("Got data for pd: {0}".format(data))
    errors = 0

    if "Enclosure Device ID" not in data:
        logger.critical("Enclosure Device ID not present in data")
        errors += 1
    elif "Slot Number" not in data:
        logger.critical("Slot Number not present in data")
        errors += 1
    else:
        errors += verify_value_and_presence("Media Error Count",
                                  "0",
                                  "Physical Disk {0}-{1}".format(data["Enclosure Device ID"], data["Slot Number"]),
                                  data)
        errors += verify_value_and_presence("Firmware state",
                                  "Online, Spun Up",
                                  "Physical Disk {0}-{1}".format(data["Enclosure Device ID"], data["Slot Number"]),
                                  data)
        errors += verify_value_and_presence("Drive has flagged a S.M.A.R.T alert",
                                  "No",
                                  "Physical Disk {0}-{1}".format(data["Enclosure Device ID"], data["Slot Number"]),
                                  data)

    return errors


def check_adapter(adapter_data):
    logger.debug("Got raw data for adapter: {0}".format(adapter_data))
    data = split_data_string(adapter_data["data"])
    logger.info("Parsing Adapter Data")
    logger.debug("Got data for adapter: {0}".format(data))
    errors = 0

    if "Adapter" not in data:
        logger.critical("Adapter not present in data")
        errors += 1
    else:
        errors += verify_value_and_presence("Memory Uncorrectable Errors",
                                  "0",
                                  "Adapter {0}".format(data["Adapter"]),
                                  data)
        errors += verify_value_and_presence("Memory Correctable Errors",
                                  "0",
                                  "Adapter {0}".format(data["Adapter"]),
                                  data)
    return errors


# Split the passed string by line
# Then split it again by :
# Handle any special cases where the second split would result in more or less than 2 values
def split_data_string(in_string):
    line_split_mod = {}
    # Split the passed string by line
    line_split = in_string.split("\n")

    # Split each part by ":"
    for line in line_split:
        string_split = line.split(":")
        string_split_mod = []

        # Remove excess whitespaces
        for string in string_split:
            if isinstance(string, str):
                string_mod = string.strip(" ")
                string_split_mod.append(string_mod)

        if len(string_split_mod) == 2:
            line_split_mod[string_split_mod[0]] = string_split_mod[1]
        else:
            logger.debug("Expected data length is 2, got {0} instead: {1}".format(len(string_split_mod), string_split_mod))
            # Handle the various cases of mispatching data length:

            # Handle the adapter
            if string_split_mod[0].startswith("Adapter"):
                adapter_split = string_split_mod[0].split()
                line_split_mod[adapter_split[0]] = adapter_split[1]
            # Handle the Virtual Drive
            elif string_split_mod[0].startswith("Virtual Drive"):
                line_split_mod[string_split_mod[0]] = string_split_mod[1] + string_split_mod[2]


    return line_split_mod


# Verify that a value is present in a dictionary,
# ensure that it matches the correct value
# and log it with the specified id_string
#
# Returns:
# 0 - If the value matches
# 1 - If the value is not found in data
# 2 - If the value is found but does not match
def verify_value_and_presence(value_name, value_correct, id_string, data):
    # Verify that the required values are present
    if value_name not in data:
        logger.critical("{0} not present in data".format(value_name))
        return 1
    else:
        value_current = data[value_name]
        # Check physical disk media error count
        if value_current != value_correct:
            logger.critical("{0} {1} not {2}: {3}".format(
                id_string,
                value_name,
                value_correct,
                value_current
            ))
            return 2
        else:
            logger.info("{0} {1} is {2}".format(
                id_string,
                value_name,
                value_current
            ))
            return 0
