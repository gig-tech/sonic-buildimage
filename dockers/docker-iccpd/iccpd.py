#!/usr/bin/python3

import signal
import subprocess
import time


class Runner:

    def __init__(self) -> None:
        self.iccpd_process: subprocess.Popen = None
        self.mlagsyncd_process: subprocess.Popen = None
        self.running = False

    def run(self):
        """
        Run mlagsyncd and iccpd, and restart them if either process terminates
        """
        signal.signal(signal.SIGTERM, self.terminate)
        self.running = True
        self.restart()
        while self.running:
            if self.mlagsyncd_process.poll() is not None or self.iccpd_process.poll() is not None and self.running:
                print("Unexpected termination of the mlagsyncd or iccpd daemon")
                self.restart()
            time.sleep(1)
    
    def restart(self):
        self.stop(wait=True)
        if self.iccpd_process and self.iccpd_process.poll() is None:
            self.iccpd_process.terminate()
            self.iccpd_process.wait()
        if self.mlagsyncd_process and self.mlagsyncd_process.poll() is None:
            self.mlagsyncd_process.terminate()
            self.mlagsyncd_process.wait()
        self.mlagsyncd_process = subprocess.Popen(["mclagsyncd"])
        self.iccpd_process = subprocess.Popen(["iccpd"])
    
    def terminate(self, signum, frame):
        self.running = False
        self.stop()
    
    def stop(self, wait=False):
        if self.iccpd_process and self.iccpd_process.poll() is None:
            self.iccpd_process.send_signal(signal.SIGKILL)
        if self.mlagsyncd_process and self.mlagsyncd_process.poll() is None:
            self.mlagsyncd_process.send_signal(signal.SIGKILL)
        if wait:
            if self.iccpd_process:
                self.iccpd_process.wait()
            if self.mlagsyncd_process:
                self.mlagsyncd_process.wait()


if __name__ == "__main__":
    runner = Runner()
    runner.run()
