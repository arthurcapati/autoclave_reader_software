import serial
import numpy as np

class SerialParser:

    @property
    def connection_is_open(self) -> bool:
        return self.__serial.is_open

    @property
    def comport(self) -> str:
        return self.__comport
    
    @comport.setter
    def comport(self, value):
        self.__comport = value
    
    @property
    def bauderate(self) -> int:
        return self.__bauderate
    
    @bauderate.setter
    def bauderate(self, value):
        self.__bauderate = value

    def __init__(self, comport:str = None , bauderate: int = None) -> None:
        self.__comport = comport
        self.__bauderate = bauderate
        self.__serial = serial.Serial(timeout=1)
        self.tempo = 0
        pass

    def connect(self):
        self.__serial.baudrate = self.bauderate
        self.__serial.port = self.comport
        self.__serial.open()

    def disconnect(self):
        self.__serial.close()

    def is_connected(self) -> bool:
        return self.__serial.is_open

    def read_serial(self):
        data = self.parse_serial()
        data = data.split(';')
        numbers = []
        columns = []
        for info in data:
            info = info.split(":")
            columns.append(info[0])
            numbers.append(float(info[-1]))

        result = {}

        for column, number in zip(columns, numbers):
            result[column] = number

        return result
    
    def parse_serial(self):
        return self.__serial.readline().decode().strip()
    
    def random(self):
        pression = np.random.randint(0, 20)
        temp = np.random.randint(25, 350)
        self.tempo = self.tempo+1

        return {"Tempo": self.tempo, "Pressão": pression, "Temperatura":temp}
