import time
import subprocess
import multiprocessing
import pandas as pd

class CameraApp:                 
    def __init__(self, time_interval, share_param):
        
        # set time interval (take a picture every N seconds)
        self.N = time_interval
        self.share_param = share_param

        # start take pictures
        self.Camera_process = multiprocessing.Process(target = self.capture_photo)
        self.Camera_process.start()
        self.timegap_ls = []
        
     
    def capture_photo(self):

        nowtime_ls = []
        
        # used for counting the times of entering while loop
        i = 0 
        
        while True:
            
            # when excuting while loop at second time, if will be activated
            if i > 0:  
                # each time the camera takes different time to take picture, therefore, here need to count the time camera spends
                time_gap = time.time() - temp_time
                print('time_gap:', time_gap)
                time.sleep(self.N - time_gap)

            temp_time = time.time()
            print("-----------------------now:", temp_time, self.share_param.num.value, self.share_param.get_img_filename())
            '''
            nowtime_ls.append(temp_time)
            '''
            subprocess.run(['libcamera-still', '--nopreview', '--timeout', '10', '-o', self.share_param.get_img_filename()], check = True)
            
            print('Finish Taking Picture!')
            self.share_param.send_event.set()
            i += 1
        '''
        df = pd.DataFrame({'take picture time': nowtime_ls})
        df.to_csv('record_take_picture.csv', index = True)
        print('average: ', np.mean(np.array(nowtime_ls)))
        print('std:', np.std(np.array(nowtime_ls)))
        '''
