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
# This is the ssh fetcher module
#
# It fetches the specified status string via ssh directly from the esx server
#
# Returns a dict with a status and a data variable

import yaml
import paramiko
import logging


class Fetcher(object):
    fetching_data = {}

    def __init__(self):
        self.logger = logging.getLogger("fetcher")

        with open('fetching.yml', 'r') as read_config:
            self.fetching_data = yaml.load(read_config)

        self.ssh = paramiko.SSHClient()
        #TODO: Verify the host key here
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.fetching_data["ssh"]["host"],
                    username=self.fetching_data["ssh"]["user"],
                    password=self.fetching_data["ssh"]["password"])
        self.logger.debug("SSH Fetcher initialized")

    def get_adapter(self, adapter_id):
        self.logger.debug("Getting Adapter Data")
        command = self.fetching_data["ssh"]["get_adapter"]
        path = self.fetching_data["ssh"]["path_megacli"]
        full_command = "cd {0} && {1}".format(path, command)

        return self.execute_command(full_command)

    def get_ld(self, ldisk_id):
        command = self.fetching_data["ssh"]["get_ld"].format(ldisk_id)
        path = self.fetching_data["ssh"]["path_megacli"]
        full_command = "cd {0} && {1}".format(path, command)

        return self.execute_command(full_command)

    def get_pd(self, array_id, pdisk_id):
        command = self.fetching_data["ssh"]["get_pd"].format(array_id,pdisk_id)
        path = self.fetching_data["ssh"]["path_megacli"]
        full_command = "cd {0} && {1}".format(path, command)

        return self.execute_command(full_command)

    def execute_command(self, full_command):
        self.logger.debug("Executing Command: {0}".format(full_command))
        stdin, stdout, stderr = self.ssh.exec_command(full_command)

        data_out = stdout.read().decode("utf-8")
        data_err = stderr.read().decode("utf-8")
        self.logger.debug("data_out: {0}".format(data_out))
        self.logger.debug("data_err: {0}".format(data_err))

        if data_err == "":
            self.logger.info("Successfully fetched data via SSH")
            return {"status": "success", "data": data_out}
        else:
            self.logger.critical("Unable to Fetch data. Error: {0}".format(data_err))
            return {"status": "error", "data": data_err}

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()
