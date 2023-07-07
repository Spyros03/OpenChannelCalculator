import tkinter as tk
import tkinter.font
from PIL import ImageTk, Image
import common
from hydrowindows import *



class MainWindow():
    

    def __init__(self):
        self.root = tk.Tk()
        self.name = 'Main'
        common.mainwin=self
        common.oppened_wins.append(self)
        self.root.geometry('1000x688')
        self.root.resizable(False, False)
        self.root.title('Open Channel Calculator')
        ico = Image.open('icon.png')
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.setmenus()
        self.setwidgets()
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()


    def setwidgets(self):
        self.image = Image.open('background.png')
        self.python_image = ImageTk.PhotoImage(self.image)
        tk.Label(self.root, image=self.python_image).place(x=0,y=0)
        buttonfont = tkinter.font.Font(name="ButtonFont", size=20, family='Arial')
        tk.Button(self.root, text='Rectangular',width=15, command=self.openrec, font=buttonfont).place(x=380, y=60)
        tk.Button(self.root, text='Triangular',width=15, command=self.opentri, font=buttonfont).place(x=380, y=160)
        tk.Button(self.root, text='Trapezoidal',width=15, command=self.opentra, font=buttonfont).place(x=380, y=260)
        tk.Button(self.root, text='Circular',width=15, command=self.opencir, font=buttonfont).place(x=380, y=360)
        tk.Button(self.root, text='Load',width=15, command=self.load, font=buttonfont).place(x=380, y=460)
        tk.Button(self.root, text='Exit',width=15, command=self.exit, font=buttonfont).place(x=700, y=570)


    def setmenus(self):
        "Sets the menus fot the GUI."
        self.menubar = tk.Menu(self.root)
        self.winmenuupdate()
        self.windowmenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_command(label='Help', command=self.help)
        self.root.config(menu=self.menubar)

    
    def winmenuupdate(self):
        self.windowmenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Window', menu=self.windowmenu)
        for win in common.oppened_wins:
            self.windowmenu.add_command(label=win.name, command=win.root.lift)


    def openrec(self):
        RectWindow()
        

    def opentri(self):
        TriWindow()


    def opentra(self):
        TrapWindow()


    def opencir(self):
        CirWindow()


    def exit(self):
        for win in common.oppened_wins[1::]:
            win.exit()
        self.root.destroy()

    
    def load(self):
        "Opens and read file."
        while True:
            fr = tkinter.filedialog.askopenfile(parent=self.root, defaultextension='.hyd', title='Open file')
            if fr is None: return #User cancelled load
            self.filename = fr.name
            fr.close
            try:
                channeltype, chan, h = hydro.Channel.read(self.filename)
                break
            except (ValueError, IOError) as e:
                tkinter.messagebox.showerror('Error','There has been an error loading the file'+ self.filename +':' + str(e))
                return
        if channeltype == 'rectangular':
            RectWindow(chan.b, h, chan.n, chan.s, self.filename)
        elif channeltype == 'trapezoidal':
            TrapWindow(math.degrees(math.atan(1/chan.t1)), math.degrees(math.atan(1/chan.t2)), chan.b, h, chan.n, chan.s, self.filename)
        elif channeltype == 'triangular':
            TriWindow(math.degrees(math.atan(1/chan.t1)), math.degrees(math.atan(1/chan.t2)), h, chan.n, chan.s, self.filename)
        elif channeltype == 'circular':
            CirWindow(chan.d, h, chan.n, chan.s, self.filename)


    def help(self):
        mes="""This program is using the Mannings formula to calculate the hydraulic properties of open channels."""
        tkinter.messagebox.showinfo('Help', mes)


if __name__ == "__main__":
    MainWindow()