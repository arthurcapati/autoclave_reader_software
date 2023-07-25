import serial.tools.list_ports as list_ports
import os

class EnvironmentVariables:

    @property
    def comports(self):
        return [port.name for port in list_ports.comports()]
    
    @property
    def actual_path(self):
        return os.getcwd()
    
Environment = EnvironmentVariables()