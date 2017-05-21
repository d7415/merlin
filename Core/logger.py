import time
import sys
from Core.config import Config

class logger:
    def __init__(self, stdout, filename):
        self.stdout = stdout
        self.logfile = file(filename, 'a')
        self.logfile.write('\n\nNew run at %s\n\n' % time.ctime())
    def write(self, text):
        self.stdout.write(text)
        self.logfile.write(time.strftime("%Y%m%d %H:%M:%S %Z | ") + text)
        self.logfile.flush()
    def close(self):
        self.stdout.close()
        self.logfile.close()

def NewLogger():
    if hasattr(sys.stdout, "logfile"):
        sys.stdout = sys.stdout.stdout
    logfile = Config.get("Misc", "debuglog")
    if not logfile in ["", "stdout"]:
        Logger = logger(sys.stdout, logfile)
        sys.stdout = Logger

NewLogger()
