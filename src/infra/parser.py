import serial
import numpy as np
import time
import pandas as pd
import json

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
        self.__bauderate = 9600
        self.__serial = serial.Serial(timeout=None)
        self.tempo = 0
        self.__last_found = ""
        pass

    def connect(self):
        self.__serial.baudrate = self.bauderate
        self.__serial.port = self.comport
        self.__serial.open()
        # self.__serial.write(str.encode("a"))

    def disconnect(self):
        self.__serial.close()

    def is_connected(self) -> bool:
        return self.__serial.is_open

    def read_serial(self) -> (pd.DataFrame, bool):
        data = self.parse_serial()
        data = f"{self.__last_found}{data}"
        found = False
        jsons = data.split("}")
        if data =="":
            data=None
        elif len(jsons)==1:
            self.__last_found = "}".join(jsons)
        else:  
            print(data)
            data = json.loads(f"{jsons[0]}"+"}")
            self.__last_found = "}".join(jsons[1:])
            # print (f'{data}')
            data = pd.DataFrame.from_dict([data])
            data.replace(to_replace=[None], value=0, inplace=True)
            print(data)
            found = True
        # print (f' Data = {data}')

        return data, found
        # if data=="":
        #     raise NotImplementedError
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

        bytesToRead = self.__serial.inWaiting()
        data=self.__serial.read(bytesToRead)
        line = data.decode()
        return line.strip()
    
    def random(self):
        pression = np.random.randint(0, 20)
        temp = np.random.randint(25, 350)
        self.tempo = self.tempo+1

        return {"Tempo": self.tempo, "Pressão": pression, "Temperatura":temp}
