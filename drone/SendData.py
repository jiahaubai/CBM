import socket
import numpy as np
import multiprocessing

class SendData:
    
    def __init__(self, HOST, PORT, share_param):
        
        
        # use TCP 
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        
        self.share_param = share_param
        self.Transmit_process = multiprocessing.Process(target = self.transmit_data)
        self.Transmit_process.start()
        
        
    def transmit_data(self):
    
        while True:
            self.share_param.send_event.wait()
            
            GPS_data = np.array(self.share_param.GPS_data[:]) #class list to numpy array
            #GPS_data[2] = 11000 # !!!!!!!!!! should be modified
            GPS_msg_bytes_len, GPS_msg_bytes = self.ArrayToBytes(GPS_data)
            
            Attitude_data = np.array(self.share_param.Attitude_data[:]) #class list to numpy array
            Att_msg_bytes_len, Att_msg_bytes = self.ArrayToBytes(Attitude_data)
            
            img_filename = self.share_param.get_img_filename()
            image_len, image_bytes = self.ImageToBytes(img_filename)
            
            print("TCP send! ", GPS_data, Attitude_data, self.share_param.get_img_filename())
            
            # send GPS message
            self.client_socket.sendall(GPS_msg_bytes_len.to_bytes(4, byteorder = 'big'))
            self.client_socket.sendall(GPS_msg_bytes)
            
            # send Attitude message
            self.client_socket.sendall(Att_msg_bytes_len.to_bytes(4, byteorder = 'big'))
            self.client_socket.sendall(Att_msg_bytes)
            
            # send image
            self.client_socket.sendall(image_len.to_bytes(4, byteorder = 'big'))
            self.client_socket.sendall(image_bytes)
            
            self.share_param.update_img_filename()
            self.share_param.send_event.clear()
            
            
    def ArrayToBytes(self, arr):

        msg_bytes = arr.tobytes()
        msg_bytes_len = len(msg_bytes)

        return msg_bytes_len, msg_bytes

    def ImageToBytes(self, file_name):

        with open(file_name, 'rb') as f:
            image_bytes = f.read()

        image_len = len(image_bytes)

        return image_len, image_bytes
