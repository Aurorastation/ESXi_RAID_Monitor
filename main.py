#
# ESXi LSI RAID Monitoring
# Copyright (C) 2017 Werner Maisl
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
import logging.config
import yaml
import parser
import fetcher.ssh as fetcher
import notifier.mail

arraydata = {"adapters": {0}, "logical_disks": {0}, "physical_disks": {252: {0, 1}}}
logdata = yaml.load(open('logging.yml', 'r'))


def main():
    status = 0
    logging.config.dictConfig(logdata)
    logger = logging.getLogger("main")
    data_fetcher = fetcher.Fetcher()
    mail_notifier = notifier.mail.Notifier()

    logger.info('Started ESXi Raid Checker')

    logger.info('Getting Adapter Data')
    # Get the data for the adapter
    for i in arraydata["adapters"]:
        status += parser.check_adapter(data_fetcher.get_adapter(i))

    logger.info('Getting LDISK Data')
    # Get the data for the logical disk
    for i in arraydata["logical_disks"]:
        status += parser.check_ld(data_fetcher.get_ld(i))

    logger.info('Getting PDISK Data')
    # Get the data for the physical disks
    for i in arraydata["physical_disks"]:
        for j in arraydata["physical_disks"][i]:
            status += parser.check_pd(data_fetcher.get_pd(i, j))

    if status == 0:
        logger.info("RAID Status Check completed without Errors")
        mail_notifier.send_notification(10)
    else:
        mail_notifier.send_notification(50)
        logger.critical("RAID Status Check completed WITH Errors. Check log for details")

if __name__ == '__main__':
    main()
