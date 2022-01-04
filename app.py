import ctypes
import win32api
import time
import multiprocessing

from random import randrange
from multiprocessing.spawn import freeze_support

import overlay # text overlaying module
import modus1, modus2, modus3, modus4, modus5, modus6, modus7 # config files

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong),
                ("y", ctypes.c_ulong)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class MouseButton:
    def __init__(self):
        self.GetKeyState = win32api.GetKeyState
        self.mouse_event = ctypes.windll.user32.mouse_event
        self.click_counter = 0
        self.left = "LEFT"
        self.right = "RIGHT"
          
    def state(self, button):
        # Left button down = 0 or 1. Button up = -127 or -128
        # Right button down = 0 or 1. Button up = -127 or -128
        left = self.GetKeyState(0x01) 
        right = self.GetKeyState(0x02)

        if button.upper() == self.left:
            if left < 0: return True
            else: return False
        
        if button.upper() == self.right:
            if right < 0: return True
            else: return False

        return False
    
    def mouse_key(self, key=None, sleep_time=None, max_click=None):
        # add from 0 to 9 ms of random delay to each press
        randomiser = float(f"0.000{randrange(0,9)}")

        # do it for the right too?
        if key.upper() == self.left:
            self.mouse_event(4, 0, 0, 0,0) # left up
            time.sleep(sleep_time+randomiser)
            
            """ keep the button state down for 'down' detection """
            if self.click_counter <= max_click-2:
                self.mouse_event(2, 0, 0, 0, 0) # left down    
                self.click_counter += 1
            else:
                self.click_counter = 0

class hotkeys:
    def __init__(self):
        self.GKS = win32api.GetKeyState
        self.modus = False

    def check(self):
        ctrl = self.GKS(0x11)
        num1 = self.GKS(0x31)
        num2 = self.GKS(0x32)
        num3 = self.GKS(0x33)
        num4 = self.GKS(0x34)
        num5 = self.GKS(0x35)
        num6 = self.GKS(0x36)
        num7 = self.GKS(0x37)

        if ctrl < 0:
            if num1 < 0:
                self.modus = modus1
                return True
            elif num2 < 0:
                self.modus = modus2
                return True
            elif num3 < 0:
                self.modus = modus3
                return True
            elif num4 < 0:
                self.modus = modus4
                return True
            elif num5 < 0:
                self.modus = modus5
                return True
            elif num6 < 0:
                self.modus = modus6
                return True
            elif num7 < 0:
                self.modus = modus7
                return True
        
        return False

class configuration:
    def __init__(self):
        """ rate of fire
            5 = ~11 per second
            4 = ~13 per second
            3 = ~16 per second
            2 = ~20 per second
            1 = ~32 per second
        """
        self.mouse_key = "left"
        self.rate_of_fire = 4 # rate of fire
        self.autoclick = False # True or False - enable autoclick
        self.click_sleep = 0.005 # 5ms
        self.max_clicks = 20 # max clicks while button down
        self.mouse_vertical = 0 # up:-1*n / down:1*n - mouse vertical correction (0 = not activated)
        self.vertical_random = 0 # variation value, goes up or down (random step - 0 = not activated
        self.mouse_horizontal = 0 # left: -1*n / right:1*n - mouse horizontal correction (0 = not activated)
        self.horizontal_random = 0 # variation value, goes left or right (random step - 0 = not activated
        self.overlay_geometry = None # use default geometry value for overlay
        self.config_name = "Modus Base"
    
    def check_move(self):
        if self.mouse_vertical != 0:
            mv = self.mouse_vertical
            if self.vertical_random != 0:
                neg_v = int(f"-{self.vertical_random}")
                mv += randrange(neg_v, self.vertical_random+1)
        else:
            mv = 0
        
        if self.mouse_horizontal != 0:
            mh = self.mouse_horizontal
            if self.horizontal_random != 0:
                neg_h = int(f"-{self.horizontal_random}")
                mh+=randrange(neg_h, self.horizontal_random+1)
        else:
            mh = 0
        
        return mh, mv
    
    def update(self, modus=None):
        self.mouse_key = modus.mouse_key
        self.rate_of_fire = modus.rate_of_fire
        self.autoclick = modus.autoclick
        self.click_sleep = modus.click_sleep
        self.max_clicks = modus.max_clicks
        self.mouse_vertical = modus.mouse_vertical
        self.vertical_random = modus.vertical_random
        self.mouse_horizontal = modus.mouse_horizontal
        self.horizontal_random = modus.horizontal_random
        self.overlay_geometry = modus.overlay_geometry
        self.config_name = modus.config_name


def move_mouse(x, y):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(x, y, 0, 0x0001, 0, ctypes.pointer(extra))
    cmd = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(cmd), ctypes.sizeof(cmd))

def main():
    mb = MouseButton()
    hk = hotkeys()
    mylay = overlay.layer()
    config = configuration()

    modus = None
    c = 0
    
    while 1:
        # "caps lock" on
        if win32api.GetKeyState(0x14):
            # check if mouse button down
            if mb.state(config.mouse_key):
                # check the polling freq
                if c==config.rate_of_fire or c==0:
                    # if autoclick is True, mouse down keeps clicking
                    if config.autoclick:
                        mb.mouse_key(config.mouse_key, config.click_sleep, config.max_clicks)
                    
                    # get mouse y,x movements and move mouse
                    mh, mv = config.check_move()
                    move_mouse(mh,mv)
                    c=0
                c+=1
            else:
                mb.click_counter = 0

        else:
            mb.click_counter = 0
        
        """ Check if hotkey compination have been pressed
            and change configuration and build layer on
            top of all screen stating the active config.
        """
        if hk.check():
            if hk.modus != modus:
                modus = hk.modus
                config.update(hk.modus)
                t = multiprocessing.Process(target=mylay.build, args=(config.config_name,config.overlay_geometry,))
                t.start()

        time.sleep(0.0001)

if __name__ == "__main__":
    freeze_support()
    main()