from tkinter import Tk, Frame, Button, Label, LEFT, RIGHT, TOP, BOTH, Entry, StringVar, DISABLED, NORMAL, filedialog
from tkinter.ttk import Combobox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.utility.utility import Environment
from src.infra.parser import SerialParser
from serial.serialutil import SerialException
import time
import numpy as np
import pandas as pd
import re


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
        self.top_widget.pack()
        self.top_widget["padx"] = 20
        self.top_widget_msg = Label(self.top_widget, text="AUTOCLAVE READER")
        self.top_widget_msg["font"] = self.object_font
        self.top_widget_msg.pack()
        pass

    def __create_connections(self, master=None):
        self.connections_main_widget = Frame(master)
        self.connections_main_widget.pack(side=LEFT)
        self.connections_main_widget["padx"] = 20

        self.com_port_main_widget = Frame(self.connections_main_widget)
        self.com_port_main_widget.pack(side=TOP)

        self.com_port_label = Label(self.com_port_main_widget, text="COM:")
        self.com_port_label["font"] = self.object_font
        self.com_port_label.pack(side=LEFT)
        
        self.com_port_combobox = Combobox(self.com_port_main_widget, width=15, textvariable=StringVar(), postcommand=self.update_comports)
        self.com_port_combobox['font'] = self.common_font
        self.update_comports()
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
        self.reader_main_widget.pack(side=LEFT)
        self.reader_main_widget["padx"] = 10

        
        self.reader_entries_widget = Frame(self.reader_main_widget)
        self.reader_entries_widget.pack()

        self.reader_entry_save_path_widget = Frame(self.reader_entries_widget)
        self.reader_entry_save_path_widget['pady'] = 10
        self.reader_entry_save_path_widget.pack()

        self.reader_entry_save_name_widget = Frame(self.reader_entries_widget)
        self.reader_entry_save_name_widget['pady'] = 10
        self.reader_entry_save_name_widget.pack()

        self.reader_buttons_widget = Frame(self.reader_entries_widget)
        self.reader_buttons_widget['pady'] = 10
        self.reader_buttons_widget.pack()

        # self.reader_save_path_label = Label(self.reader_entry_save_path_widget, text="Save To:")
        # self.reader_save_path_label["font"] = self.object_font
        # self.reader_save_path_label.pack(side=LEFT)

        # self.reader_save_path_entry = Entry(self.reader_entry_save_path_widget)
        # self.reader_save_path_entry["width"] = 50
        # self.reader_save_path_entry['font'] = self.common_font
        # content = StringVar()
        # content.set(Environment.actual_path)
        # self.reader_save_path_entry['textvariable'] = content
        # self.reader_save_path_entry.pack(side=LEFT)

        # self.reader_save_path_label = Label(self.reader_entry_save_name_widget, text="Save Name:")
        # self.reader_save_path_label["font"] = self.object_font
        # self.reader_save_path_label.pack(side=LEFT)

        # self.reader_save_path_entry = Entry(self.reader_entry_save_name_widget)
        # self.reader_save_path_entry["width"] = 50
        # self.reader_save_path_entry['font'] = self.common_font
        # content = StringVar()
        # content.set("entry.csv")
        # self.reader_save_path_entry['textvariable'] = content
        # self.reader_save_path_entry.pack(side=LEFT)

        

        self.reader_start_button = Button(self.reader_buttons_widget)
        self.reader_start_button["text"] = "Start"
        self.reader_start_button["font"] = self.object_font
        self.reader_start_button["width"] = 12
        self.reader_start_button["command"] = self.start_reading
        self.reader_start_button['state'] = DISABLED
        self.reader_start_button.pack(side=LEFT)

        self.reader_stop_button = Button(self.reader_buttons_widget)
        self.reader_stop_button["text"] = "Stop"
        self.reader_stop_button["font"] = self.object_font
        self.reader_stop_button["width"] = 12
        self.reader_stop_button["command"] = self.stop_reading
        self.reader_stop_button['state'] = DISABLED
        self.reader_stop_button.pack(side=LEFT)

        self.reader_save_button = Button(self.reader_buttons_widget)
        self.reader_save_button["text"] = "Save"
        self.reader_save_button["font"] = self.object_font
        self.reader_save_button["width"] = 12
        self.reader_save_button["command"] = self.save_data
        self.reader_save_button['state'] = DISABLED
        self.reader_save_button.pack(side=LEFT)

        


    def __create_vizualization(self, master=None):
        self.vizualization_main_widget = Frame(master)
        # self.vizualization_main_widget.grid(column=0, row=3)
        self.vizualization_main_widget.pack(side=TOP)
        self.vizualization_main_widget["padx"] = 20
        # self.vizualization_main_widget_msg = Label(self.vizualization_main_widget, text="AQUI ESTARA O GRAFICO DA LEITURA")
        # self.vizualization_main_widget_msg["font"] = self.common_font
        # self.vizualization_main_widget_msg.pack()

        plt.ion()

        color='blue'
        self.figure = plt.Figure(figsize=(6, 5), dpi=150)
        self.ax = self.figure.add_subplot(111)
        self.line_pression, = self.ax.plot(0,0, color=color)
        self.ax.set_ylabel('Pressão (bar)', color=color)  # we already handled the x-label with ax1
        self.ax.tick_params(axis='y', color=color)
        self.ax.yaxis.label.set_color(color)
        self.ax.spines['left'].set_color(color)
        self.ax.spines['left'].set_linewidth(1)
        self.ax.tick_params(axis = "y",colors=color, which="both")
        self.ax.autoscale(True)
        self.ax.set_xlim(0,10)
        self.ax.set_ylim(-1,10)

        color='red'
        self.ax2 = self.ax.twinx() 
        self.ax2.set_ylabel('Temperatura (°C)', color=color)  # we already handled the x-label with ax1
        self.line_temperature, = self.ax2.plot(0,0, color=color)
        self.ax2.autoscale(True)
        self.ax2.yaxis.label.set_color(color)
        self.ax2.spines['right'].set_color(color)
        self.ax2.tick_params(colors=color, which='both')
        self.ax2.set_ylim(-1, 30)
        self.ax2.tick_params(axis='y', color=color)

        self.figure.tight_layout() 

        self.figure_canvas = FigureCanvasTkAgg(self.figure, self.vizualization_main_widget)
        self.figure_canvas.get_tk_widget().pack(side=LEFT, fill=BOTH)

        self.ax.set_title('Data')

    def update_comports(self):
        comports = Environment.comports
        self.com_port_combobox['values'] = comports
        if len(comports)>1:
            self.com_port_combobox.current(0)
        self.com_port_combobox.pack()
        pass

    def connect_to_comport(self):
        try:
            self.serial_parser.bauderate = self.baudrate
            self.serial_parser.comport = self.comport
            self.serial_parser.connect()

            self.connection_button["text"] = "Disconnect"
            self.connection_button["bg"] = "#078f22"
            self.connection_button["command"] = self.disconnect_to_comport

            self.reader_start_button['state'] = NORMAL

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

        self.reader_start_button['state'] = DISABLED

        pass

    def start_reading(self):
        self.reader_start_button['state'] = DISABLED
        self.reader_stop_button['state'] = NORMAL
        self.reader_save_button['state'] = DISABLED
        self.__reading = True

        self.__clear_data()

        self.serial_parser.parse_serial()
        while self.serial_parser.is_connected() and self.reading:
            time.sleep(0.2)
            self.update()
            
            data, found = self.serial_parser.read_serial()
            
            if found:
                self.data_frame = pd.concat([self.data_frame, data], ignore_index=True).dropna()
                self.__update_graph()

    def __clear_data(self):
        self.data = []
        self.data_frame = self.data_frame.drop(self.data_frame.index)

    def __update_graph(self):
        tempo = self.data_frame["Tempo"].values
        pression = self.data_frame["Pressao"].values
        temperature = self.data_frame["Temperatura"].values

        self.line_pression.set(ydata=pression, xdata=tempo)
        self.__update_ax_limits(self.ax, tempo, pression)

        self.line_temperature.set(ydata=temperature, xdata=tempo)
        self.__update_ax_limits(self.ax2, tempo, temperature)

        self.figure_canvas.draw()
        self.figure_canvas.flush_events()


    def __update_ax_limits(self, ax, xdata, ydata):
        max_x_value = self.__find_upper_limit(max(xdata))
        max_y_value = self.__find_upper_limit(max(xdata))
        ax.set_xlim(min(xdata), max_x_value)
        ax.set_ylim(0, max_y_value)

    def __find_upper_limit(self, max_value) -> int:
        if max_value<10:
            blocks = (max_value//1) + 1
            return blocks
        elif max_value<50:
            blocks = (max_value//5) + 1
            return blocks*5
        elif max_value<100:
            blocks = (max_value//10) + 1
            return blocks*10
        elif max_value<1000:
            blocks = (max_value//100) + 1
            return blocks*100
        else:
            blocks = (max_value//1000) + 1
            return blocks*1000

    def stop_reading(self):
        self.reader_start_button['state'] = NORMAL
        self.reader_stop_button['state'] = DISABLED
        self.reader_save_button['state'] = NORMAL
        self.__reading = False
 

    def save_data(self):
        data = [('All tyes(*.*)', '*.*'),("csv file(*.csv)","*.csv")]
        filename = filedialog.asksaveasfile(initialfile="entry.csv", initialdir=Environment.actual_path, filetypes = data, defaultextension = data)

        if filename:
            self.data_frame.to_csv(filename.name)


        
