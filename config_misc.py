import time
import os

class MyConfigWrap:
    def __init__(self, pfn:str):
        import configparser
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = lambda option:option
        self.filename = pfn
        rd = self.conf.read(pfn)
        if not rd:
            self.generate_default()
    
    def generate_default(self, force=False):
        if self.conf.sections() and not force:
            return
        import platform
        pdir = os.path.dirname(self.filename)
        dct = {
            "default": {
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'), 
                "author": os.getlogin(), 
                "agent": ' '.join(['pcsnap', 'browtory', '0.0.1', 'python', platform.python_version(), platform.system(), platform.version(), platform.machine()]), 
                # "database": DB,
                "log_file": os.path.join(pdir, 'vanager.log'),
                "name": "vanager", 
                # "runlog_file": 'vanager_{{timestamp}}.log',
                "user_id": 0
            }
        }
        self.conf.read_dict(dct)   
        self.conf.write(open(self.filename, 'w'))

    def update(self, key, value):
        dct = {"default": {"updated_at": time.strftime('%Y-%m-%d %H:%M:%S'), key:value}}
        self.conf.read_dict(dct)   
        self.conf.write(open(self.filename, 'w'))

    def get(self, section, option, **kwargs):
        return self.conf.get(section, option, **kwargs)

    def getint(self, section, option, **kwargs):
        return self.conf.getint(section, option, **kwargs)

    def section_to_dict(self, section:str):
        secs = self.conf.options(section)
        dct = {}
        for k in secs:
            dct[k] = self.conf.get(section, k)
        return dct

    def to_dict(self):
        dct = {}
        for sec in self.conf.sections():
            secs = self.conf.options(sec)
            sdct = {}
            for k in secs:
                sdct[k] = self.conf.get(sec, k)
            dct[sec] = sdct
        return dct

def getLogger(name:str, level="INFO", disable=False, log_file="procWatcher.log"):
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.disabled = disable
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))  # create a logging format
        logger.addHandler(handler)  # add the handlers to the logger
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))  # create a logging format
        logger.addHandler(console)
    return logger
