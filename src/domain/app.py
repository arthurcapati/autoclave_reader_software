from tkinter import Tk, Frame, Button, Label, LEFT, RIGHT, TOP, BOTH, Entry, StringVar, DISABLED, NORMAL
from tkinter.ttk import Combobox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.utility.utility import Environment
from src.infra.parser import SerialParser
from serial.serialutil import SerialException
import time
import numpy as np
import pandas as pd
# from tkinter import ttk
# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()


class Application(Frame):

    @property
    def common_font(self):
        return ("Verdana", "10")
    
    @property
    def object_font(self):
        return ("Verdana", "14", "italic", "bold")
    
    @property
    def error_font(self):
        return ("Verdana", "9", "italic", "bold")
    
    @property
    def comport(self) -> str:
        return self.com_port_combobox.get()
    
    @property
    def baudrate(self) -> int:
        return int(self.baud_port_entry.get())
    
    @property
    def reading(self) -> int:
        return self.__reading


    def __init__(self, master=None):
        super().__init__(master)

        self.__create_top(master)
        self.top_frame  = Frame(master)
        self.top_frame.pack()
        self.com_frame  = Frame(self.top_frame)
        self.com_frame.pack(side=LEFT)
        self.reader_frame  = Frame(self.top_frame)
        self.reader_frame.pack(side=RIGHT)
        self.__create_connections(self.com_frame)
        self.__create_reader(self.reader_frame)

        self.data_json = {}
        self.data_frame = pd.json_normalize(self.data_json)

        self.__create_vizualization(master)

        self.serial_parser = SerialParser()
        
    
    def __create_top(self, master=None):
        self.top_widget = Frame(master)
        # self.top_widget.grid(column=0, row=0)
        self.top_widget.pack()
        self.top_widget["padx"] = 20
        self.top_widget_msg = Label(self.top_widget, text="AUTOCLAVE READER")
        self.top_widget_msg["font"] = self.object_font
        self.top_widget_msg.pack()
        pass

    def __create_connections(self, master=None):
        self.connections_main_widget = Frame(master)
        # self.connections_main_widget.grid(column=0, row=1)
        self.connections_main_widget.pack(side=LEFT)
        self.connections_main_widget["padx"] = 20
        # self.connections_main_widget_msg = Label(self.connections_main_widget, text="AQUI ESTARA A CONEXÃO POR USB E POR BLUETOOH")
        # self.connections_main_widget_msg["font"] = ("Verdana", "14", "italic", "bold")
        # self.connections_main_widget_msg.pack()

        self.com_port_main_widget = Frame(self.connections_main_widget)
        self.com_port_main_widget.pack(side=TOP)

        self.com_port_label = Label(self.com_port_main_widget, text="COM:")
        self.com_port_label["font"] = self.object_font
        self.com_port_label.pack(side=LEFT)
        
        self.com_port_combobox = Combobox(self.com_port_main_widget, width=15, textvariable=StringVar())
        self.com_port_combobox['font'] = self.common_font
        self.com_port_combobox['values'] = Environment.comports
        self.com_port_combobox.current(0)
        self.com_port_combobox.pack()

        self.baud_port_main_widget = Frame(self.connections_main_widget)
        self.baud_port_main_widget.pack(side=TOP)

        self.baud_port_label = Label(self.baud_port_main_widget, text="BAUDRATE:")
        self.baud_port_label["font"] = self.object_font
        self.baud_port_label.pack(side=LEFT)
        
        self.baud_port_entry = Entry(self.baud_port_main_widget)
        self.baud_port_entry["width"] = 10
        self.baud_port_entry['font'] = self.common_font
        content = StringVar()
        content.set('9600')
        self.baud_port_entry['textvariable'] = content
        self.baud_port_entry.pack(side=LEFT)

        self.connection_button = Button(self.connections_main_widget)
        self.connection_button["text"] = "Connect"
        self.connection_button["font"] = self.object_font
        self.connection_button["width"] = 12
        self.connection_button["command"] = self.connect_to_comport
        self.connection_button.pack(side=LEFT)

        self.connection_error_label = Label(self.connections_main_widget, text="", wraplength=500, pady=20)
        self.connection_error_label["font"] = self.error_font
        self.connection_error_label.pack(side=LEFT)

    def __create_reader(self, master=None):
        self.reader_main_widget = Frame(master)
        # self.reader_main_widget.grid(column=0, row=2)
        self.reader_main_widget.pack(side=LEFT)
        self.reader_main_widget["padx"] = 10
        # self.reader_main_widget_msg = Label(self.reader_main_widget, text="LEITURA")
        # self.reader_main_widget_msg["font"] = ("Verdana", "14", "italic", "bold")
        # self.reader_main_widget_msg.pack()
        
        self.reader_entries_widget = Frame(self.reader_main_widget)
        self.reader_entries_widget.pack()

        self.reader_entry_path_widget = Frame(self.reader_entries_widget)
        self.reader_entry_path_widget['pady'] = 10
        self.reader_entry_path_widget.pack()

        self.reader_buttons_widget = Frame(self.reader_entries_widget)
        self.reader_buttons_widget['pady'] = 10
        self.reader_buttons_widget.pack()

        self.reader_save_path_label = Label(self.reader_entry_path_widget, text="Save To:")
        self.reader_save_path_label["font"] = self.object_font
        self.reader_save_path_label.pack(side=LEFT)

        self.reader_save_path_entry = Entry(self.reader_entry_path_widget)
        self.reader_save_path_entry["width"] = 50
        self.reader_save_path_entry['font'] = self.common_font
        content = StringVar()
        content.set(Environment.actual_path)
        self.reader_save_path_entry['textvariable'] = content
        self.reader_save_path_entry.pack(side=LEFT)

        self.reader_start_button = Button(self.reader_buttons_widget)
        self.reader_start_button["text"] = "Start"
        self.reader_start_button["font"] = self.object_font
        self.reader_start_button["width"] = 12
        self.reader_start_button["command"] = self.start_reading
        self.reader_start_button.pack(side=LEFT)

        self.reader_stop_button = Button(self.reader_buttons_widget)
        self.reader_stop_button["text"] = "Stop"
        self.reader_stop_button["font"] = self.object_font
        self.reader_stop_button["width"] = 12
        self.reader_stop_button["command"] = self.stop_reading
        self.reader_stop_button['state'] = DISABLED
        self.reader_stop_button.pack(side=LEFT)

        


    def __create_vizualization(self, master=None):
        self.vizualization_main_widget = Frame(master)
        # self.vizualization_main_widget.grid(column=0, row=3)
        self.vizualization_main_widget.pack(side=TOP)
        self.vizualization_main_widget["padx"] = 20
        self.vizualization_main_widget_msg = Label(self.vizualization_main_widget, text="AQUI ESTARA O GRAFICO DA LEITURA")
        self.vizualization_main_widget_msg["font"] = self.common_font
        self.vizualization_main_widget_msg.pack()

        plt.ion()
        self.figure = plt.Figure(figsize=(6, 5), dpi=150)
        self.ax = self.figure.add_subplot(111)
        self.lines, = self.ax.plot(0,0)
        self.ax.autoscale(True)
        self.ax.set_xlim(0,10)
        self.ax.set_ylim(0,100)
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self.vizualization_main_widget)
        self.figure_canvas.get_tk_widget().pack(side=LEFT, fill=BOTH)

        self.ax.set_title('Data')


    def connect_to_comport(self):
        try:
            self.serial_parser.bauderate = self.baudrate
            self.serial_parser.comport = self.comport
            self.serial_parser.connect()

            self.connection_button["text"] = "Disconnect"
            self.connection_button["bg"] = "#078f22"
            self.connection_button["command"] = self.disconnect_to_comport

        except SerialException as error:
            self.connection_error_label['text'] = error.args[0]
            self.connection_button["bg"] = "#b01507"
        except Exception as error:
            self.connection_error_label['text'] = "Not Connected"
            self.connection_button["bg"] = "#b01507"
            pass

    def disconnect_to_comport(self):
        try:
            self.serial_parser.disconnect()
        except:
            pass

        self.connection_button["text"] = "Connect"
        self.connection_button["command"] = self.connect_to_comport
        self.connection_button["bg"] = "SystemButtonFace"

        pass

    def start_reading(self):
        self.reader_start_button['state'] = DISABLED
        self.reader_stop_button['state'] = NORMAL
        self.__reading = True

        self.data = []
        self.data_frame = self.data_frame.drop(self.data_frame.index)

        while self.serial_parser.is_connected() and self.reading:
            self.update()
            data = self.serial_parser.random()
            self.data_frame = pd.concat([self.data_frame, pd.json_normalize(data)], ignore_index=True).dropna()
            xdata = self.data_frame.iloc[:,0].values
            ydata = self.data_frame.iloc[:,1].values
            self.lines.set(ydata=ydata, xdata=xdata)
            self.auto_scale(max(xdata), max(ydata))
            self.figure_canvas.draw()
            self.figure_canvas.flush_events()
            # self.data.append(self.serial_parser.read_serial())

    def auto_scale(self, x_lim,y_lim):
        # if self.ax.get_xlim()[1]<x_lim:
        self.ax.set_xlim(0,x_lim)
        # if self.ax.get_xlim()[1]<y_lim:
        self.ax.set_ylim(0,y_lim)
        pass



    def stop_reading(self):
        self.reader_start_button['state'] = NORMAL
        self.reader_stop_button['state'] = DISABLED
        self.__reading = False

        self.data

        
