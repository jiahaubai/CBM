import argparse
import multiprocessing
import time
from FlyController import FlyController
from Camera import CameraApp
from SendData import SendData

class SharedParam:
    
    def __init__(self):
        
        # used for saving the info of GPS and Attitude which gotten from Fly controller currently
        self.GPS_data = multiprocessing.Array('d', [-1.0, -1.0, -1.0]) # default setting [lon, lat, alt]
        self.Attitude_data = multiprocessing.Array('d', [-1.0, -1.0, -1.0]) # default setting [roll, pitch, yaw]
        
        # used for writteing image file name
        self.num = multiprocessing.Value('i', 0)
        self.img_filename = multiprocessing.Array('b', b"./images/photo_0.jpg" + b" " *5)
        print(bytes(self.img_filename[:]).decode())
        
        # create the event which used for calling the func transmit_data in class SendData
        # after excuting the func capture_photo in class CameraApp
        self.send_event = multiprocessing.Event() 
    
    def update_img_filename(self):
        with self.num.get_lock():
            self.num.value += 1
        with self.img_filename.get_lock():
            new_filename = f"./images/photo_{self.num.value}.jpg".encode()
            self.img_filename[:len(new_filename)] = new_filename
            
    def get_img_filename(self):
        return bytes(self.img_filename[:]).decode()


def main():
    
    # set the shared parameters
    share_param = SharedParam()
    '''
    i = 0
    while i < 12:
        share_param.update_img_filename()
        print(i, share_param.get_img_filename())
        time.sleep(1)
        i += 1
    '''
    
    # set Camera
    time_interval = 5
    CAM = CameraApp(time_interval, share_param)
    
    # set Fly controller
    serial_port = '/dev/ttyUSB0'
    baudrate = 115200
    FC = FlyController(serial_port, baudrate, share_param)
    
    # set the TCP client
    HOST = "192.168.50.53"
    PORT = 5000
    SD = SendData(HOST, PORT, share_param)
    
    '''
    time_interval = args.time
    CAM = CameraApp(time_interval)
    
    # set Fly controller
    serial_port = args.serial_port
    baudrate = args.baudrate
    FC = FlyController(serial_port, baudrate)
    
    # set the TCP client
    HOST = args.host_ip
    PORT = args.host_port
    SD = SendData(HOST, PORT)
    '''                
    
if __name__ == "__main__":
    
    # input argument
    parser = argparse.ArgumentParser(description="Input Argument")
    
    parser.add_argument('-t', '--time', type = int, help = 'time interval of taking pictures')
    parser.add_argument('-sp', '--serial_port', type = str, help = 'Fly controller serial port')
    parser.add_argument('-b', '--baudrate', type = int, help = 'Baudrate of Fly controller serial port')
    parser.add_argument('-hi', '--host_ip', type = str, help = 'Host IP')
    parser.add_argument('-hp', '--host_port', type = int, help = 'Host port')
    
    args = parser.parse_args()
    
    main()
    


        
        
        


