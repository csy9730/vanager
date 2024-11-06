import time
import math

class FooRunner:
    def __init__(self):
        self.is_running = None
        self.data = []
        self._idx = -1
        self.stop_at = 999999999999999
        self.begin_at = 999999999999999

    def start(self):
        tm = int(time.time())
        self.data = [{"data":i, "timestamp": tm + i} for i in range(15)]
        self.is_running = True
        self.begin_at = tm
        self.stop_at = tm + 20

    def stop(self):
        self.is_running = False
        self.stop_at = int(time.time())
        # self.begin_at = 999999999999999

    def getState(self, idx:int, tm:int):
        i = 0
        for i, d in enumerate(self.data[idx:]):
            if tm < d["timestamp"]:
                break
        idx2 = idx + i + 1
        print(idx, idx2, i, self.data)
        return self.data[idx:idx2]

    # def getRecentState(self):
    #     self._idx += 1
    #     return self._idx, self.data[self._idx]
    
    # def getRunning(self):
    #     return self.is_running
    
    def getRunning(self, ts:int):
        if ts < self.begin_at:
            # self.stop_at:
            return None
        elif ts < self.stop_at:
            # return self.is_running
            return True
        else:
            return False


from zmc.motion.lookahead_motion import MotionLookahead
from zmc.pather.linear import LinearPathPlanner
from zmc.speeder.scurveBase import VelocityType

class ZmcRunner:
    def __init__(self):
        self.is_running = None
        self.data = []
        self._idx = -1
        self.stop_at = 999999999999999
        self.begin_at = 999999999999999
        self.mc = MotionLookahead(is_relative=False)

        self.mc.setVelocityParams(V_m=2, A_m=1, A_n=1, S_p=5, velocType=VelocityType.VELOC_SCURVE_J, merge=True)
        self.is_first = True

    def add_cmd(self):
        tm = int(time.time()) + 0.25
        if self.is_first:
            self.begin_at = tm      
            self.is_first = False  
            dt = 0
        else:
            dt = tm - self.begin_at
        self.mc.append_path(LinearPathPlanner([15, 10], is_relative=True), tm=dt)
        self.mc.build()
        self.stop_at = tm + self.mc.get_total_period()
        self.is_running = True

    # def start(self):
        # self.data = [{"data":i, "timestamp": tm + i} for i in range(15)]

    def stop(self):
        # self.is_running = False
        dt = time.time() + 0.25 - self.begin_at
        self.mc.move_stop(dt)
        self.mc.build()
        self.stop_at = math.ceil(self.mc.get_total_period())
        # int(time.time())
        # self.begin_at = 999999999999999

    def getState(self, idx:int, tm:int):
        mc = self.mc
        import math
        dt = tm - self.begin_at
        pt = mc.get_total_period()
        pt = min([pt, dt])
        Ts = 0.25
        N = math.ceil(pt/Ts)

        tt, sx, sy = [], [], []
        
        for i in range(idx, N):
            t = i*Ts
            pos = mc.get_postion(t)
            v = mc.get_rate(t)
            tt.append(t)
            sx.append(pos[0])
            sy.append(pos[1])
            print(i, t, *pos, v)
        idx2 = idx + len(tt)
        print(idx, idx2)
        return {'tt': tt, 'sx': sx, 'sy': sy, 'next_ofs': idx2}

    # def getRecentState(self):
    #     self._idx += 1
    #     return self._idx, self.data[self._idx]
    
    # def getRunning(self):
    #     return self.is_running
    
    def getRunning(self, ts:int):
        if ts < self.begin_at:
            # self.stop_at:
            return None
        elif ts < self.stop_at:
            # return self.is_running
            return True
        else:
            return False
                