import os
import sys
import os.path as osp
from argparse import Namespace
import subprocess
from typing import Optional, List, Dict
import functools


def genCmdline(cmds, dct={}):
    import jinja2
    tmpl = jinja2.Template(cmds)
    return tmpl.render(**dct)


def genCmdline_demo():
    cmdline = "{{pythonPath2}} -m imageCls.lib.trainerCli -i {{trainPath}} {% if validPath %}-v {{validPath}}{% endif %} -eo {{experPath}} {% if epochs %}--epochs {{epochs}} {% endif %} {% if batch_size %} --batch-size {{batch_size}} {% endif %} {% if arch %} --arch {{arch}} {% endif %} {% if resume %} --resume{% endif %}"
    params = {"pythonPath2":"python", "trainPath":"dataset/cat_dog","epochs": "5"}
    cmd = genCmdline(cmdline, params)
    print(cmd)

def run_cmd(cmds:str, cwd=None):
    rt = subprocess.run(cmds, shell=True, capture_output=True, cwd=cwd)
    return rt

def cmdRun(cmds, outfile=None, cwd=None):
    if outfile:
        stdout = open(outfile, 'w')
    else:
        stdout = subprocess.PIPE
    ret = subprocess.call(cmds, stdout=stdout, cwd=cwd)
    return ret

def popen_cmd(cmd, outfile=None):
    g_pop = subprocess.Popen(cmd, shell=True, stdout=open(outfile, 'w'), stderr=subprocess.STDOUT)
    return g_pop

def cmdPopen(cmds:List[str], outfile:Optional[str]=None, cwd:Optional[str]=None, shell=False):
    if outfile:
        stdout = open(outfile, 'w')
    else:
        stdout = subprocess.PIPE
    if os.name == "posix":
        # cmd_path_dic = {'Path':'%Path%' + ROOTPATH + "/bin"} # env=cmd_path_dic, 
        shell_flag   = True
        result = subprocess.Popen(cmds, shell=shell, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable="/bin/bash")
    else:
        cmd_path_dic = None
        shell_flag = False  
        result = subprocess.Popen(cmds, cwd=cwd, bufsize=64000, shell=shell, stdout=stdout, stderr=subprocess.STDOUT)
    return result


import signal
def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    import psutil
    assert pid != os.getpid(), "won't kill myself"

    if psutil.pid_exists(pid):        
        parent = psutil.Process(pid)    
        # print(parent)        
    else:
        return None, None

    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)

from enum import IntEnum
class EnPopWrapStat(IntEnum):
    PROC_NOT_FOUND = 0
    PROC_RUNNING = 1
    PROC_FINISHED = 2
    PROC_KILLED = 3
    PROC_STARTED_ERROR = -1  # CrashExit
    PROC_ERROR_STOP = -2 # CrashExit

class PopWrap:
    def __init__(self):
        self._pop:Optional[subprocess.Popen] = None
        self._stat = EnPopWrapStat.PROC_NOT_FOUND
        self._outfile = None
        self._returncode = None

    def is_running(self):
        return self._stat == EnPopWrapStat.PROC_RUNNING

    def to_dict(self):
        return {"returncode": self._returncode, "outfile": self._outfile, 
                "stat": self._stat, "pid": self._pop.pid if self._pop else None}
    
    @staticmethod
    def genByCmdline(cmd, outfile=None, cwd=None, shell=False):
        popw = PopWrap()
        try:
            popw._pop = cmdPopen(cmd, outfile=outfile, cwd=cwd, shell=shell)
        except (FileNotFoundError, ZeroDivisionError) as e:
            print(e)
            popw._stat = EnPopWrapStat.PROC_STARTED_ERROR
            return popw
        except Exception as e:
            print(e)
            popw._stat = EnPopWrapStat.PROC_STARTED_ERROR
            return popw
        popw._outfile = outfile
        popw._stat = EnPopWrapStat.PROC_RUNNING
        return popw
    
    def setPopen(self, pop):
        self._pp = pop

    def getOutFile(self):
        return self._outfile

    def checkIsRunning(self):
        """
            检查程序是否退出，
                通过 poll 查询，可以获得 returncode
                通过 psutil 查询，无法获得 returncode
        """
        if self._pop:
            if EnPopWrapStat.PROC_RUNNING != self._stat:
                # self._returncode = self._pop.returncode
                return
            ret = self._pop.poll()
            if ret is None:
                return
            else:
                self._returncode = ret
                self._stat = EnPopWrapStat.PROC_FINISHED
                return EnPopWrapStat.PROC_FINISHED
        else:
            if self._stat:
                return self._stat
            self._stat = EnPopWrapStat.PROC_NOT_FOUND
            return EnPopWrapStat.PROC_NOT_FOUND

    def kill_popen(self):
        if self._pop:
            if EnPopWrapStat.PROC_RUNNING != self._stat:
                return self._stat
            ret = self._pop.poll()
            if ret is None:
                kill_proc_tree(self._pop.pid, signal.SIGTERM)
                ret = self._pop.poll()
                if ret is None:
                    return EnPopWrapStat.PROC_RUNNING
                else:
                    self._returncode = ret
                    self._stat = EnPopWrapStat.PROC_KILLED
                    return EnPopWrapStat.PROC_KILLED
            else:
                self._stat = EnPopWrapStat.PROC_FINISHED
                self._returncode = self._pop.returncode
                return EnPopWrapStat.PROC_FINISHED
        else:
            self._stat = EnPopWrapStat.PROC_NOT_FOUND
            return EnPopWrapStat.PROC_NOT_FOUND
        
class PopWrapMgr:
    def __init__(self):
        self._pops:Dict[str][PopWrap] = {}
        self._idx = 0
        self._recent = None

    def addCmdline(self, cmd:str, outfile=None, cwd=None):
        popw = PopWrap.genByCmdline(cmd, outfile=outfile, cwd=cwd)
        self._pops[self._idx] = popw
        self._idx += 1

    def put(self, uid, pp:PopWrap):
        self._pops[uid] = pp
        self._idx += 1
        self._recent = uid

    def get(self, uid) -> PopWrap:
        return self._pops.get(uid, PopWrap())

    def kill(self, uid):
        return self.get(uid).kill_popen()

def popwrap_demo():
    cmd = ["ping","localhost"]
    pw = PopWrap.genByCmdline(cmd)
    import time
    for i in range(10):
        ret = pw.checkIsRunning()
        if ret != EnPopWrapStat.PROC_RUNNING:
            print(i, ret)  
            break
        time.sleep(0.5)
    print(pw._pop.returncode, pw._pop.pid)        
        
def popwrap_kill_demo():
    cmd = ["ping","localhost"]
    pw = PopWrap.genByCmdline(cmd)
    import time
    for i in range(10):
        if i == 5:
            ret = pw.kill_popen()
        else:
            ret = pw.checkIsRunning()
        if ret != EnPopWrapStat.PROC_RUNNING:
            print(i, ret)  
        time.sleep(0.5)
    print(pw._pop.returncode, pw._pop.pid)   

def popwrap_error_demo():
    cmd = "pinglocalhost"
    pw = PopWrap.genByCmdline(cmd)
    import time
    for i in range(10):
        ret = pw.checkIsRunning()
        # if ret != EnPopWrapStat.PROC_RUNNING:
        print(i, ret)  
        time.sleep(0.5)
    print(pw._returncode) 

def genLines(fl, offset=0):
    fl.seek(offset, 0)
    lines = fl.readlines()
    # for line in lines:
    #     yield line.decode('gbk')
    return lines, fl.tell()

def genNonempty(lines):
    for ln in lines:
        if ln in ['\n', '\r', ' ', '']:
            pass
        else:
            yield ln.strip('\r').strip('\n')
   


def readFileContent(filename, offset=0, limit=-1, is_byte=True, use_line=None, encoding = "utf8"):
    with open(filename, 'rb') as fp:
        fp.seek(offset, 0)
        if use_line:
            rd = fp.readlines(limit)
        else:
            if limit <= 0: limit = None
            rd = fp.read(limit)
        ends = fp.tell()
    dct = {"offset": offset, "ends":ends}
    if not is_byte and not use_line:
        dct = {"text": rd.decode(encoding), "offset":offset, "ends":ends}
    elif not is_byte and use_line:
        dct = {"lines": [ln.decode(encoding) for ln in rd], "offset":offset, "ends":ends}
    elif is_byte and use_line:
        dct = {"contents": rd, "offset":offset, "ends":ends}
    else:
        dct = {"content": rd, "offset":offset, "ends":ends}
    return dct
    # TypeError: Object of type 'bytes' is not JSON serializable

def readFileContent_demo():
    dct = readFileContent(__file__, limit=10, use_line=True, is_byte=False)
    print(dct)
    dct = readFileContent(__file__, limit=11, use_line=True, is_byte=False)
    print(dct)
    dct = readFileContent(__file__, limit=-1, use_line=True, is_byte=False)
    print(dct)
    dct = readFileContent(__file__, limit=-1, use_line=False, is_byte=False)
    # print(dct)
    
def readFileContent_rl_demo():
    offset = 0
    for i in range(10):
        dct = readFileContent(__file__, offset=offset, limit=4410, use_line=True, is_byte=False)
        print(dct)
        offset = dct["ends"]


if __name__ == "__main__":
    # genCmdline_demo()
    popwrap_demo()
    # popwrap_kill_demo()
    # popwrap_error_demo()
    # readFileContent_demo()
    # readFileContent_rl_demo()