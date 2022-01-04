import tkinter as Tkinter
import win32api, win32con, pywintypes

class layer:
    def exit(self):
        self.label.quit()
        self.label.destroy()

    def build(self, text=None, geometry=None):
        self.label = Tkinter.Label(text=text, font=('Calibri','14'), fg='white', bg='black')
        self.label.master.overrideredirect(True)
        if geometry != None:
            self.label.master.geometry(geometry)
        else:
            self.label.master.geometry("+250+250")
        self.label.master.lift()
        self.label.master.wm_attributes("-topmost", True)
        self.label.master.wm_attributes("-disabled", True)
        #label.master.wm_attributes("-transparentcolor", "green")

        hWindow = pywintypes.HANDLE(int(self.label.master.frame(), 16))
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
        # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

        self.label.pack()
        self.label.after(1000, lambda: self.exit())
        self.label.mainloop()

if __name__ == "__main__":
    mylay2 = layer()
    mylay2.build('Modus Mini m14')