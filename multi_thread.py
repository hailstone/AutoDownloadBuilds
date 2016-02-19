import threading
import time

__author__ = 'haokai'


class MultiThreadDownloading():
    def __init__(self, max_thread):
        self.job_num = 0
        self.max_thread = max_thread

    def add_job(self, target_function, download_url, local_dir, undownloaded_list):

        while threading.activeCount() > self.max_thread:
            # print "thread pool is full now, wait for 30s"
            time.sleep(1)

        # time.sleep(1)
        print "\n%dth job begin" % self.job_num
        t = threading.Thread(target=target_function, args=(download_url, local_dir, undownloaded_list))
        t.start()
        self.job_num += 1

