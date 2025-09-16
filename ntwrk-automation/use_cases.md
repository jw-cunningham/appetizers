# Use Cases
- **push-config.py** to push configuration to any appliance supported by netmiko device types
  * example: update the SNMP stack for all of the cisco_ios devices in your network
- **pull-config.py**  to retrieve state information or running-config from any appliance supported by netmiko device types
  * example: backup all of the cisco_ios running-configs in your network daily/nightly
- **parser.sh** to scan any directory for desired syntax, or the lackthereof
  * example: find all of the devices within your network that are missing a specific line of config that have been backed up by pull-config.py
