import socket
import numpy as np
import piexif
import time


def transfer_DegMinSec(origin_coordinate):
    deg = int(origin_coordinate)
    
    ori_min = (origin_coordinate - deg)*60
    min = int(ori_min)
    
    ori_sec = (ori_min - min)*60
    sec = int(ori_sec*100000)
    
    return deg, min, sec

def write_GPSExif(lon_deg, lon_min, lon_sec,
               lat_deg, lat_min, lat_sec,
               alt,
               file_name):
    
    # img = Image.open("rcv_test_image.jpg")       # 使用 PIL Image 開啟圖片
    # exif = piexif.load(img.info["exif"])   # 使用 piexif 讀取圖片 Exif 資訊
    
    if alt < 0:
        print("Error: altitude value is negative.")
    
    gps_ifd = {
        piexif.GPSIFD.GPSLongitude: ((lon_deg, 1), (lon_min, 1), (lon_sec, 100000)),
        piexif.GPSIFD.GPSLatitude: ((lat_deg, 1), (lat_min, 1), (lat_sec, 100000)), 
        piexif.GPSIFD.GPSAltitude: (alt, 1000)
    }

    exif_dict = {"GPS": gps_ifd}
    piexif.insert(piexif.dump(exif_dict), file_name)
    #print("Finish Writing GPS Exif!")
    
def write_Attitude_Exif(roll, pitch, yaw, file_name):
    # 讀取原始 EXIF 資訊
    exif_dict = piexif.load(file_name)
    '''
    # 將 roll, yaw, pitch 資訊轉為 JSON 格式
    custom_data = {
        "Roll": roll,
        "Pitch": pitch,
        "Yaw": yaw
    }
    custom_data_json = json.dumps(custom_data)
    
    # 添加到 UserComment 欄位 (EXIF ID: 37510)
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = custom_data_json.encode("utf-8")
    '''
    description = f"Roll={roll}, Yaw={yaw}, Pitch={pitch}"
    exif_dict["0th"][piexif.ImageIFD.XPComment] = description.encode("utf-16le")
    
    # 將修改後的 EXIF 資訊寫回圖片
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)
    #print("Finish Writing Attitude Exif!")

def recv_exact(conn, size):
    """確保接收指定大小的資料"""
    data = b""
    while len(data) < size:
        packet = conn.recv(size - len(data))
        if not packet:
            raise ConnectionError("Stop connection!")
        data += packet
    return data

def recv_file(conn, num):
    # 接收GPS訊息
    GPSmsg_bytes_len = int.from_bytes(conn.recv(4), byteorder='big')
    GPSmsg_bytes = recv_exact(conn, GPSmsg_bytes_len)
    GPSdecode_msg = np.frombuffer(GPSmsg_bytes)
    #print(f"Receive GPS message: {GPSdecode_msg}")
    
    if GPSmsg_bytes_len == 0:
        return False
    
    
    # 接收無人機姿態
    Attmsg_bytes_len = int.from_bytes(conn.recv(4), byteorder='big')
    Attmsg_bytes = recv_exact(conn, Attmsg_bytes_len)
    Attdecode_msg = np.frombuffer(Attmsg_bytes)
    #print(f"Receive Att message: {Attdecode_msg}")
    
    if Attmsg_bytes_len == 0:
        return False
    
    
    
    # 接收圖片
    image_bytes_len = int.from_bytes(conn.recv(4), byteorder='big')
    image_data = recv_exact(conn, image_bytes_len)  # 根據長度讀取圖片內容
    #print(f"Receive image: {image_bytes_len} bytes")
    
    if image_bytes_len == 0:
        return False

    # 保存圖片到本地
    file_name = "./images/received_" + str(num) + ".jpg"
    with open(file_name, "wb") as f:
        f.write(image_data)
    print(f"Save image {num}: {image_bytes_len} bytes", time.time())


    # 寫入Exif
    lon = GPSdecode_msg[0]
    lat = GPSdecode_msg[1]
    alt = int(GPSdecode_msg[2])

    lon_deg, lon_min, lon_sec = transfer_DegMinSec(lon)
    lat_deg, lat_min, lat_sec = transfer_DegMinSec(lat)

    
    write_GPSExif(lon_deg, lon_min, lon_sec,lat_deg, lat_min, lat_sec, alt, file_name)
    
    roll = Attdecode_msg[0]
    pitch = Attdecode_msg[1]
    yaw = Attdecode_msg[2]
    
    write_Attitude_Exif(roll, pitch, yaw, file_name)
    
    
    return True

# 設置server端
HOST = '0.0.0.0'
PORT = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST,PORT))
server_socket.listen(5)

print("Server is activated and is waiting for connect...")
conn, addr = server_socket.accept()
print(f"Success connect to: {addr}")

num = 1
receive_flag = True

while receive_flag:
        receive_flag = recv_file(conn, num)
        num += 1

'''
try:
    while receive_flag:
        receive_flag = recv_file(conn, num)
        num += 1
except Exception as e:
    print(f"Stop Connection: {e}")
finally:
    conn.close()
    server_socket.close()
    print("Close the server!")
'''