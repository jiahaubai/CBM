import multiprocessing
import numpy as np
from pymavlink import mavutil
import argparse

class FlyController:
    
    def __init__(self, serial_port, baudrate, share_param):
        
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.share_param = share_param
        
        self.the_connection = mavutil.mavlink_connection(serial_port, baud=self.baudrate)
        self.the_connection.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (self.the_connection.target_system, self.the_connection.target_component))
        
        if self.the_connection.target_system:
        
            self.GPS_process = multiprocessing.Process(target = self.getGPSInfo)
            self.Att_process = multiprocessing.Process(target = self.getAttitude)
            self.GPS_event = multiprocessing.Event()
            self.Att_event = multiprocessing.Event()
            # Although the func self.getGPSInfo and func self.getAttitude are executed in turn
            # the time gap between their execution is 0.0001 sec.
                
            self.GPS_process.start()
            self.Att_process.start()
        
    
    def getGPSInfo(self):
        
        global code_running
        global GPS_data
        
        while True:
            
            # get GPS data
            self.GPS_event.wait()
            msg = self.the_connection.recv_match(type='GPS_RAW_INT', blocking=True)
            
            if msg is not None:
                
                longitude = (msg.lon)*1e-7
                latitude = (msg.lat)*1e-7
                altitude = msg.alt
                with self.share_param.GPS_data.get_lock():
                    self.share_param.GPS_data[:] = [longitude, latitude, altitude]
                    
            print("GPS: ", self.share_param.GPS_data[:])
            # Add the stop code constraint
            # once the drone close to the last flight path point
            
            self.GPS_event.clear()
            self.Att_event.set()
            
            
    def getAttitude(self):
        
        global code_running
        global Attitude_data
        
        while True:
            
            # get Attitude data
            msg = self.the_connection.recv_match(type='ATTITUDE', blocking=True)
            
            if msg is not None:
                roll = msg.roll
                pitch = msg.pitch
                yaw = msg.yaw
                with self.share_param.Attitude_data.get_lock():
                    self.share_param.Attitude_data[:] = [roll, pitch, yaw]
            
            print("Attitude: ", self.share_param.Attitude_data[:])
            self.GPS_event.set()
            self.Att_event.wait()
            self.Att_event.clear()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Input Argument")
    
    parser.add_argument('-sp', '--serial_port', type = str, help = 'Fly controller serial port')
    parser.add_argument('-b', '--baudrate', type = int, help = 'Baudrate of Fly controller serial port')
    args = parser.parse_args()
    
    # set Fly controller
    serial_port = args.serial_port
    baudrate = args.baudrate
    FC = FlyController(serial_port, baudrate)
    

