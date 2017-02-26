This script is used to monitor the RAID status of a ESXi Server.
The Free ESXi Server has no notification capabilities,
therefore I decided to write this script to get notified if there are any issues with the RAID.
It can either read the status via local files that are copied to the monitoring machine from the ESXi Server
or automatically get the status from the ESX.

This is room to expand this script, but for now it works and it is sufficient for my needs.
It also is fairly configurable and it is possible to adapt this for other RAID Controllers with a bit of effort.

Thanks goes to JetBrains for their PyCharm IDE

Dependencies: yaml, paramiko