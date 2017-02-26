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
#
# This is the mail notifier module for the ESXi Raid Monitoring Script
#
# It notifies based upon the settings in the notification.yml
import logging
import yaml
import smtplib
import time

class Notifier(object):
    notification_data = {}

    def __init__(self):
        self.logger = logging.getLogger("notifier")
        with open('notification.yml', 'r') as read_config:
            self.notification_data = yaml.load(read_config)

    # Function to send a notification
    def send_notification(self, level):
        # Send notifications for each specified method
        time_current = time.time()
        time_notification_last = float(self.notification_data["mail"]["time_last"])
        time_notification_interval = float(self.notification_data["mail"]["time_interval"])
        time_passed = time_current - time_notification_last

        if level >= self.notification_data["mail"]["level_minimum"]:
            self.logger.debug("Level exceeding minimum level: {0}".format(level))
            if time_passed > time_notification_interval:
                self.logger.debug("Notification interval exceeded: {0}".format(time_passed))
                self.notification_data["mail"]["time_last"] = time_current
                with open('notification.yml', 'w') as write_config:
                    yaml.dump(self.notification_data, write_config)

                self.send_mail(level)
        elif level >= self.notification_data["mail"]["level_required"]:
            self.logger.debug("Level exceeding required level: {0}".format(level))
            self.send_mail(level)

    # Sends a E-Mail Notification
    def send_mail(self, level):
        self.logger.debug("Sending Mail")
        server = smtplib.SMTP(self.notification_data["mail"]["server"], self.notification_data["mail"]["port"])
        # server.set_debuglevel(1)
        server.ehlo("mail.my.net")
        server.starttls()
        server.login(self.notification_data["mail"]["user"], self.notification_data["mail"]["password"])
        message = self.generate_notification_message(level)
        try:
            server.sendmail(self.notification_data["mail"]["sender"], self.notification_data["mail"]["recipients"], message)
            self.logger.debug("Successfully sent Mail")
        except smtplib.SMTPException:
            self.logger.critical("Unable to send Mail")
        server.quit()

    # Generating a notification message to be sent
    def generate_notification_message(self, level):
        mail_from = "{0} <{1}>".format(self.notification_data["server_name"], self.notification_data["mail"]["sender"])
        mail_to = ", ".join(self.notification_data["mail"]["recipients"])
        mail_subject = "{0} Raid Status Report - {1}".format(self.notification_data["server_name"], level)
        mail_message = "RAID Status Report from {0}:\r\n".format(self.notification_data["server_name"])
        mail_message += self.fetch_logfile_data()

        body = """From: {0}
    To: {1}
    Subject: {2}
    
    {3}""".format(mail_from, mail_to, mail_subject, mail_message)
        return body

    # Fetching the log file data to be sent with the notification message
    def fetch_logfile_data(self):
        file = open("monitoring.log", "r")
        return file.read()
