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
# This is the filesystem fetcher module for the ESXi Raid Monitoring Script
#
# It fetches the specified status file from the file system and returns the output of it
#
# Returns a dict with a status and a data variable

import os
import time
import stat
import logging
import yaml


class Fetcher(object):
    fetching_data = {}

    def __init__(self):
        self.logger = logging.getLogger("fetcher")
        with open('fetching.yml', 'r') as read_config:
            self.fetching_data = yaml.load(read_config)
        self.logger.debug("File Fetcher initialized")

    def get_adapter(self, adapter_id):
        self.logger.debug("Getting Adapter Data")
        file_name = "raidstatus_{0}_adapterinfo_{1}".format(self.fetching_data["file"]["prefix"], adapter_id)
        contents = self.get_file_contents(file_name, self.fetching_data["file"]["path"])
        return contents


    def get_ld(self, ldisk_id):
        file_name = "raidstatus_{0}_ldinfo_{1}".format(self.fetching_data["file"]["prefix"], ldisk_id)
        contents = self.get_file_contents(file_name, self.fetching_data["file"]["path"])
        return contents


    def get_pd(self, array_id, pdisk_id):
        file_name = "raidstatus_{0}_pdinfo_{1}_{2}".format(self.fetching_data["file"]["prefix"], array_id, pdisk_id)
        contents = self.get_file_contents(file_name, self.fetching_data["file"]["path"])
        return contents


    def get_file_contents(self, file_name, path):
        file_path = path + file_name
        for entry in os.scandir(path):
            if entry.name == file_name:
                # Got a file
                self.logger.debug("Found entry for file {0}".format(file_path))

                # Check if the creation time is within the specified timeframe
                timediff = time.time() - os.stat(file_path)[stat.ST_MTIME]
                if timediff > self.fetching_data["file"]["maxage"]:
                    self.logger.error("File {0} has a timediff exceeding the max allowed timediff {1} - {2}".
                                 format(file_name, timediff, self.fetching_data["file"]["maxage"]))
                    return {"status": "failed", "data": "Maximum Time Exceeded"}

                # Return the contents of the file
                file = open(file_path, 'r')
                str = file.read()
                file.close()
                return {"status": "success", "data": str}

        self.logger.error("Found no file matching {0}".format(self.fetching_data["file"]["path"]))
        return {"status": "error", "data": "File not found"}
