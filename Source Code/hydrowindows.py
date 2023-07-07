import tkinter as tk
import tkinter.font, tkinter.messagebox, tkinter.filedialog
import hydro, common, math
from PIL import ImageTk, Image



class RectWindow:

    
    def __init__(self, b=4.00, h=5.00, n=0.015, s=0.5, name='untitled '):
        "Initilize the window."
        self.root = tk.Toplevel(common.mainwin.root)
        common.oppened_wins.append(self)
        if name == 'untitled ':
            self.name = name + str(len(common.oppened_wins)-1)
        else:
            self.name = name
            self.filename = name
        ico = Image.open('icon.png')
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.rownumber = 2
        self.filename = None
        self.depthmode = False
        self.statepar = [b, h, n, s] 
        self.setfonts()
        self.setmenus()
        self.makewidgets()
        self.draw(b, h)
        self.winmenuupdate()
        self.update()
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.title(self.name)
        self.initvalues(h, b, s, n)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()

    @staticmethod
    def newrec():
        RectWindow()
        
    @staticmethod
    def newtrap():
        TrapWindow()

    @staticmethod
    def newtri():
        TriWindow()

    @staticmethod
    def newcir():
        CirWindow()
    
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


    def initvalues(self, h, b, s, n):
        "Sets the initial values"
        self.entDepth.delete(0, 'end')
        self.entDepth.insert(0, str(h))
        self.entWidth.delete(0, 'end')
        self.entWidth.insert(0, str(b))
        self.entSlope.delete(0, 'end')
        self.entSlope.insert(0, str(s))
        self.entManning.delete(0, 'end')
        self.entManning.insert(0, str(n))

    
    def save(self):
        "Saves the file to the already loaded file."
        if self.filename == None:
            self.saveas()
        else:
            values = self.getvalues()
            if values == None: return
            self.savetofile(self.filename, values)
    
    
    def saveas(self):
        "Saves the file to a selected file."
        values = self.getvalues()
        if values == None: return
        fr = tkinter.filedialog.asksaveasfile(parent=self.root, defaultextension='.hyd', title="Select file to Save.")
        if fr == None: return #User cancelled.
        self.filename = fr.name
        self.name = self.filename
        self.root.title(self.filename)
        self.update()
        fr.close
        self.savetofile(self.filename, values)

   
    def savetofile(self, fr, values):
        "Writes to the file when called."
        b , h , n, s = values
        chan = hydro.RectChannel(s, n, b)
        try:
            chan.write(fr, h)
            self.statepar = values
        except IOError as e:
                tkinter.messagebox.showerror('Error', str(e))
                self.saveas()
                return


    def togglemode(self):
        for ent in [self.entWidth, self.entDepth, self.entSlope, 
                    self.entManning, self.entVel, self.entDis]:
            ent.config(state='normal')
        if self.depthmode == True:
            self.modelab.config(text='Mode: Normal')
            self.depthmode = False
        else:
            self.depthmode = True
            self.modelab.config(text='Mode: Depth')
        if self.depthmode:
            self.entDepth.config(state='readonly')
        else:
            self.entDis.config(state='readonly')
        self.entVel.config(state='readonly')
        
       
    def getvalues(self, depthmode=False, showerrors=True):
        "Gets the values from the entries"
        values = []
        b = self.checkvalues(self.entWidth, vmin=0.001, vmax=10000, showerrors=showerrors)
        if b == None:
            return
        values.append(b)
        if depthmode:
            h = self.checkvalues(self.entDis)
        else:
            h = self.checkvalues(self.entDepth, vmin=0, vmax=220,showerrors=showerrors)
        if h == None:
            return
        values.append(h)
        n = self.checkvalues(self.entManning, vmin=0.001, vmax=0.1, showerrors=showerrors)
        if n == None:
            return
        values.append(n)
        s = self.checkvalues(self.entSlope,  vmin=0.01, vmax=1000, showerrors=showerrors)
        if s == None:
            return
        values.append(s)
        return values
    
    
    def checkvalues(self, ent, vmin=None, vmax=None, showerrors=False):
        try: value = float(ent.get().replace(',','.'))
        except: value = None
        if showerrors:
            if value == None: 
                tkinter.messagebox.showwarning("Error", "A value is missing")
                ent.focus_set()
                return None
            if vmin is not None:
                if value < vmin:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
                elif value > vmax:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
        return value


    def setresults(self, results, depthmode=False):
        "Sets the results"
        if self.depthmode:
            ent = self.entDepth
        else:
            ent = self.entDis
        ent.config(state='normal')
        ent.delete(0, 'end')
        ent.insert(0, str(results[1]))
        ent.config(state='readonly')
        self.entVel.config(state='normal')
        self.entVel.delete(0, 'end')
        self.entVel.insert(0, str(results[0]))
        self.entVel.config(state='readonly')


    def setfonts(self):
        "Sets the font for the GUI."
        defaultfont = tkinter.font.Font(name="TkDefaultFont", exists=True)
        defaultfont.config(size=20, family='Arial')
        textfont = tkinter.font.Font(name="TkTextFont", exists=True)
        textfont.config(family="Arial", size=20)
        fixedfont = tkinter.font.Font(name="TkFixedFont", exists=True)
        fixedfont.config(size=20)
        captionfont = tkinter.font.Font(name="TkCaptionFont", exists=True)
        captionfont.config(size=14)
        menufont = tkinter.font.Font(name="TkMenuFont", exists=True)
        menufont.config(size=20)
        self.buttonfont=tkinter.font.Font(size=16, family='Arial')


    def setmenus(self):
        "Sets the menus fot the GUI."
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", menu=filemenu)
        newmenu = tk.Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='New', menu=newmenu)
        filemenu.add_command(label='Load', command=self.load)
        filemenu.add_command(label='Save', command=self.save)
        filemenu.add_command(label='Save As', command=self.saveas)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.exit)
        newmenu.add_command(label='Rectangular', command=self.newrec)
        newmenu.add_command(label='Triangular', command=self.newtri)
        newmenu.add_command(label='Trapezoidal', command=self.newtrap)
        newmenu.add_command(label='Circular', command=self.newcir)
        self.winmenuupdate()
        self.menubar.add_command(label='Help', command=self.help)
        self.root.config(menu=self.menubar)

    
    def winmenuupdate(self):
        self.windowmenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Window', menu=self.windowmenu)
        for win in common.oppened_wins:
            self.windowmenu.add_command(label=win.name, command=win.root.lift)


    def update(self):
        for win in common.oppened_wins:
            win.setmenus()


    def labentry(self, rownumber, desc, def_value=''):
        "Creates a label with an entry next to it."
        lab = tk.Label(self.root, text=desc)
        lab.grid(row=rownumber, column=0, sticky='e')
        ent = tk.Entry(self.root, width=18)
        ent.grid(row=rownumber, column=1,  sticky='we')
        ent.insert(0, def_value)
        return ent


    def makewidgets(self):
        "Initilizes the Widgets."
        lab = tk.Label(self.root, text='School of Civil Engineering', foreground='green')
        lab.grid(row=0, column=0, columnspan=2)
        lab = tk.Label(self.root, text='Rectangular', foreground='green')
        lab.grid(row=0, column=2)
        self.canvas = tk.Canvas(self.root, background='darkgrey', height=200, width=500)
        self.canvas.grid(row=1, column=0, columnspan=3, sticky='wesn')
        self.rownumber += 1 
        self.entWidth = self.labentry(self.rownumber, "Width (m):", '4.00')
        self.modelab = tk.Label(self.root, text='Mode: Normal',width= 15)
        self.modelab.grid(row=self.rownumber, column=2)
        self.rownumber += 1  
        togglebutton = tk.Button(self.root, text='Toggle', command=self.togglemode, font=self.buttonfont)
        togglebutton.grid(row=self.rownumber, column=2)
        self.entDepth = self.labentry(self.rownumber, "Depth (m):", '5.00')
        self.rownumber += 1 
        self.entSlope = self.labentry(self.rownumber, "Slope(%):", '0.5')
        self.rownumber += 1 
        self.entManning = self.labentry(self.rownumber, "Manning:", '0.015')
        self.rownumber += 1
        compute = tk.Button(self.root, text='Compute', command=self.compute, font=self.buttonfont)
        compute.grid(row=self.rownumber, column=2)
        self.entVel = self.labentry(self.rownumber, "Velocity (m/s):", '')
        self.rownumber += 1
        self.entDis = self.labentry(self.rownumber, "Discharge (m3/s):", '')
        self.entVel.config(state='readonly')
        self.entDis.config(state='readonly')

    def draw(self, b, h):
        "Draw the open channel."
        dc = self.canvas
        dc.update_idletasks() # _idletasks breaks WinDoze 98 support
        dcw = dc.winfo_width() # Pixels
        dch = dc.winfo_height() # Pixels
        if dcw < 2 or dch < 2: return #tkinter reported wrong width or height
        #perx = dcw*0.05 #Margin x
        pery = dch*0.05 #Margin y
        dcwef = dcw# - 2*perx #Effective width is now smaller
        dchef = dch - 2*pery #Effective height is now smaller
        dc.delete(tk.ALL) # Clear window
        hchan = h*1.1 #Height of channel is bigger than water level
        bchan = b
        akl = dcwef/bchan
        akly= dchef/hchan
        if akly < akl: akl = akly
        perx = dcw/2 - akl*(b/2) #Margin x
        def topix(x, y): return perx+x*akl, dch-(pery+y*akl)
        cs = ( (0, 0), (b, h) ) #Draw water surface
        cs = [topix(x, y) for x, y in cs]
        dc.create_rectangle(cs, fill="cyan", outline=None, stipple="gray25")
        cs = ( (0, h), (b, h) ) #Draw water level
        cs = [topix(x, y) for x, y in cs]
        dc.create_line(cs, fill="blue", width=3)
        cs = ( (0, hchan), (0, 0), (bchan, 0), (bchan, hchan) ) #Draw channel
        cs = [topix(x, y) for x, y in cs]
        dc.create_line(cs, fill="brown", width=3) 

    def compute(self, depthmode=False):
        values = self.getvalues(depthmode=self.depthmode)
        if values == None: return
        b ,h, n, s = values
        s /= 100
        channel = hydro.RectChannel(s, n, b)
        if self.depthmode:
            v, q = channel.depth(h)
            self.draw(b, q)
        else: 
            v, q = channel.discharge(h)
            self.draw(b, h)
        self.setresults((v,q))


    def exit(self):
        if not self.ok2quit():
            return
        common.oppened_wins.remove(self)
        self.root.destroy()
        self.update()
        del self.entWidth, self.entDepth, self.entDis
        del self.entSlope, self.entManning, self.entVel

    
    def ok2quit(self):
        if self.statepar != self.getvalues(depthmode=False, showerrors=False):
            r = tk.messagebox.askokcancel("Data is not saved",
            "ok to abandon changes?", default="cancel", parent=self.root)
            return r 
        else: return True

        
    def help(self):
        mes="""This program is using the Mannings formula to calculate the hydraulic properties of open channels."""
        tkinter.messagebox.showinfo('Help', mes)


class TrapWindow():
    def __init__(self, t1=45.0, t2=45.0, b=4.00, h=5.00, n=0.015, s=0.5, name='untitled '):
        "Initilize the window."
        self.root = tk.Toplevel(common.mainwin.root)
        common.oppened_wins.append(self)
        if name == 'untitled ':
            self.name = name + str(len(common.oppened_wins)-1)
        else:
            self.name = name
            self.filename = name.split('/')[-1]
        ico = Image.open('icon.png')
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.rownumber = 2
        self.filename = None
        self.depthmode = False
        self.statepar = [t1, t2, b, h, n, s] 
        self.setfonts()
        self.setmenus()
        self.makewidgets()
        self.draw(b, h, t1, t2)
        self.winmenuupdate()
        self.update()
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.title(self.name)
        self.initvalues(t1, t2, h, b, s, n)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()

    @staticmethod
    def newrec():
        RectWindow()
        
    @staticmethod
    def newtrap():
        TrapWindow()

    @staticmethod
    def newtri():
        TriWindow()

    @staticmethod
    def newcir():
        CirWindow()
    
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


    def initvalues(self, t1, t2, h, b, s, n):
        "Sets the initial values"
        self.entDepth.delete(0, 'end')
        self.entDepth.insert(0, str(h))
        self.entWidth.delete(0, 'end')
        self.entWidth.insert(0, str(b))
        self.entSlope.delete(0, 'end')
        self.entSlope.insert(0, str(s))
        self.entManning.delete(0, 'end')
        self.entManning.insert(0, str(n))
        self.entt1.delete(0, 'end')
        self.entt1.insert(0, str(t1))
        self.entt2.delete(0, 'end')
        self.entt2.insert(0, str(t2))

    
    def save(self):
        "Saves the file to the already loaded file."
        if self.filename == None:
            self.saveas()
        else:
            values = self.getvalues()
            if values == None: return
            self.savetofile(self.filename, values)
    
    
    def saveas(self):
        "Saves the file to a selected file."
        values = self.getvalues()
        if values == None: return
        fr = tkinter.filedialog.asksaveasfile(parent=self.root, defaultextension='.hyd', title="Select file to Save.")
        if fr == None: return #User cancelled.
        self.filename = fr.name
        self.name = self.filename
        self.root.title(self.filename)
        self.update()
        fr.close
        self.savetofile(self.filename, values)

   
    def savetofile(self, fr, values):
        "Writes to the file when called."
        t1d , t2d, b, h, n, s = values
        t1 = 1/math.tan(math.radians(t1d))
        t2 = 1/math.tan(math.radians(t2d))
        chan = hydro.TrapezChannel(s, n, b, t1, t2)
        try:
            chan.write(fr, h)
            self.statepar = values
        except IOError as e:
                tkinter.messagebox.showerror('Error', str(e))
                self.saveas()
                return


    def togglemode(self):
        for ent in [self.entWidth, self.entDepth, self.entSlope, 
                    self.entManning, self.entVel, self.entDis]:
            ent.config(state='normal')
        if self.depthmode == True:
            self.modelab.config(text='Mode: Normal')
            self.depthmode = False
        else:
            self.depthmode = True
            self.modelab.config(text='Mode: Depth')
        if self.depthmode:
            self.entDepth.config(state='readonly')
        else:
            self.entDis.config(state='readonly')
        self.entVel.config(state='readonly')
        
       
    def getvalues(self, depthmode=False, showerrors=True):
        "Gets the values from the entries"
        values = []
        t1 = self.checkvalues(self.entt1, vmin=0.0, vmax=179.0, showerrors=showerrors)
        if t1 == None:
            return
        values.append(t1)
        t2 = self.checkvalues(self.entt2, vmin=0.0, vmax=179.0, showerrors=showerrors)
        if t2 == None:
            return
        values.append(t2)
        b = self.checkvalues(self.entWidth, vmin=0.001, vmax=10000, showerrors=showerrors)
        if b == None:
            return
        values.append(b)
        if depthmode:
            h = self.checkvalues(self.entDis)
        else:
            h = self.checkvalues(self.entDepth, vmin=0.00, vmax=220,showerrors=showerrors)
        if h == None:
            return
        values.append(h)
        n = self.checkvalues(self.entManning, vmin=0.001, vmax=0.1, showerrors=showerrors)
        if n == None:
            return
        values.append(n)
        s = self.checkvalues(self.entSlope,  vmin=0.01, vmax=1000, showerrors=showerrors)
        if s == None:
            return
        values.append(s)
        return values
    
    
    def checkvalues(self, ent, vmin=None, vmax=None, showerrors=False):
        try: value = float(ent.get().replace(',','.'))
        except: value = None
        if showerrors:
            if value == None: 
                tkinter.messagebox.showwarning("Error", "A value is missing")
                ent.focus_set()
                return None
            if vmin is not None:
                if value < vmin:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
                elif value > vmax:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
        return value


    def setresults(self, results, depthmode=False):
        "Sets the results"
        if self.depthmode:
            ent = self.entDepth
        else:
            ent = self.entDis
        ent.config(state='normal')
        ent.delete(0, 'end')
        ent.insert(0, str(results[1]))
        ent.config(state='readonly')
        self.entVel.config(state='normal')
        self.entVel.delete(0, 'end')
        self.entVel.insert(0, str(results[0]))
        self.entVel.config(state='readonly')


    def setfonts(self):
        "Sets the font for the GUI."
        defaultfont = tkinter.font.Font(name="TkDefaultFont", exists=True)
        defaultfont.config(size=20, family='Arial')
        textfont = tkinter.font.Font(name="TkTextFont", exists=True)
        textfont.config(family="Arial", size=20)
        fixedfont = tkinter.font.Font(name="TkFixedFont", exists=True)
        fixedfont.config(size=20)
        captionfont = tkinter.font.Font(name="TkCaptionFont", exists=True)
        captionfont.config(size=14)
        menufont = tkinter.font.Font(name="TkMenuFont", exists=True)
        menufont.config(size=20)
        self.buttonfont=tkinter.font.Font(size=16, family='Arial')


    def setmenus(self):
        "Sets the menus fot the GUI."
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", menu=filemenu)
        newmenu = tk.Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='New', menu=newmenu)
        filemenu.add_command(label='Load', command=self.load)
        filemenu.add_command(label='Save', command=self.save)
        filemenu.add_command(label='Save As', command=self.saveas)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.exit)
        newmenu.add_command(label='Rectangular', command=self.newrec)
        newmenu.add_command(label='Triangular', command=self.newtri)
        newmenu.add_command(label='Trapezoidal', command=self.newtrap)
        newmenu.add_command(label='Circular', command=self.newcir)
        self.winmenuupdate()
        self.menubar.add_command(label='Help', command=self.help)
        self.root.config(menu=self.menubar)

    
    def winmenuupdate(self):
        self.windowmenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Window', menu=self.windowmenu)
        for win in common.oppened_wins:
            self.windowmenu.add_command(label=win.name, command=win.root.lift)


    def update(self):
        for win in common.oppened_wins:
            win.setmenus()


    def labentry(self, rownumber, desc, def_value=''):
        "Creates a label with an entry next to it."
        lab = tk.Label(self.root, text=desc)
        lab.grid(row=rownumber, column=0, sticky='e')
        ent = tk.Entry(self.root, width=18,)
        ent.grid(row=rownumber, column=1,  sticky='we')
        ent.insert(0, def_value)
        return ent


    def makewidgets(self): 
        "Initilizes the Widgets."
        lab = tk.Label(self.root, text='School of Civil Engineering', foreground='green')
        lab.grid(row=0, column=0, columnspan=2)
        lab = tk.Label(self.root, text='Trapezoidal', foreground='green')
        lab.grid(row=0, column=2)
        self.canvas = tk.Canvas(self.root, background='darkgrey', height=200, width=500)
        self.canvas.grid(row=1, column=0, columnspan=3, sticky='wesn')
        self.rownumber += 1 
        self.entt1 = self.labentry(self.rownumber, 'LAngle (deg):')
        self.modelab = tk.Label(self.root, text='Mode: Normal',width= 15)
        self.modelab.grid(row=self.rownumber, column=2)
        self.rownumber += 1 
        self.entt2 = self.labentry(self.rownumber, 'RAngle (deg):')
        togglebutton = tk.Button(self.root, text='Toggle', command=self.togglemode, font=self.buttonfont)
        togglebutton.grid(row=self.rownumber, column=2)
        self.rownumber += 1 
        self.entWidth = self.labentry(self.rownumber, "Width (m):", '4.00')
        self.rownumber += 1  
        self.entDepth = self.labentry(self.rownumber, "Depth (m):", '5.00')
        self.rownumber += 1 
        self.entSlope = self.labentry(self.rownumber, "Slope(%):", '0.5')
        self.rownumber += 1 
        self.entManning = self.labentry(self.rownumber, "Manning:", '0.015')
        self.rownumber += 1
        compute = tk.Button(self.root, text='Compute', command=self.compute, font=self.buttonfont)
        compute.grid(row=self.rownumber, column=2)
        self.entVel = self.labentry(self.rownumber, "Velocity (m/s):", '')
        self.rownumber += 1
        self.entDis = self.labentry(self.rownumber, "Discharge (m3/s):", '')
        self.entVel.config(state='readonly')
        self.entDis.config(state='readonly')

    def draw(self, b, h , t1, t2):
        "Draw the open channel."
        dc = self.canvas
        dc.update_idletasks() # _idletasks breaks WinDoze 98 support
        dcw = dc.winfo_width() # Pixels
        dch = dc.winfo_height() # Pixels
        if dcw < 2 or dch < 2: return #tkinter reported wrong width or height
        #perx = dcw*0.05 #Margin x
        pery = dch*0.05 #Margin y
        dcwef = dcw# - 2*perx #Effective width is now smaller
        dchef = dch - 2*pery #Effective height is now smaller
        dc.delete(tk.ALL) # Clear window
        hchan = h*1.1 #Height of channel is bigger than water level
        bchan = b
        akl = dcwef/(bchan + 2*hchan/math.tan(t1*math.pi/180))
        akly= dchef/hchan
        if akly < akl: akl = akly
        perx = dcw/2 - akl*(bchan/2) #Margin x
        def topix(x, y): return perx+x*akl, dch-(pery+y*akl)
        cs = ((-h/math.tan(t1*math.pi/180), h), (0, 0), (b, 0), (b + h/math.tan(t2*math.pi/180), h)) #Draw water surface
        cs = [topix(x, y) for x, y in cs]
        dc.create_polygon(cs, fill="cyan", outline=None, stipple="gray25")
        cs = ((-h/math.tan(t1*math.pi/180), h), (b+h/math.tan(t2*math.pi/180), h)) #Draw water level
        cs = [topix(x, y) for x, y in cs]
        dc.create_line(cs, fill="blue", width=3)
        cs = ( (-hchan/math.tan(t1*math.pi/180), hchan), (0, 0), (bchan, 0), (bchan + hchan/math.tan(t2*math.pi/180), hchan) ) #Draw channel
        cs = [topix(x, y) for x, y in cs]
        dc.create_line(cs, fill="brown", width=3) 

    def compute(self, depthmode=False):
        values = self.getvalues(depthmode=self.depthmode)
        if values == None: return
        t1d, t2d, b ,h, n, s = values
        s /= 100
        t1 = 1/math.tan(math.radians(t1d))
        t2 = 1/math.tan(math.radians(t2d))
        channel = hydro.TrapezChannel(s, n, b, t1, t2)
        if self.depthmode:
            v, q = channel.depth(h)
            self.draw(b, q, t1d, t2d)
        else: 
            v, q = channel.discharge(h)
            self.draw(b, h, t1, t2)
        self.setresults((v,q))


    def exit(self):
        if not self.ok2quit():
            return
        common.oppened_wins.remove(self)
        self.root.destroy()
        self.update()
        del self.entWidth, self.entDepth, self.entDis
        del self.entSlope, self.entManning, self.entVel
        del self.entt1, self.entt2
    
    def ok2quit(self):
        if self.statepar != self.getvalues(depthmode=False, showerrors=False):
            r = tk.messagebox.askokcancel("Data is not saved",
            "ok to abandon changes?", default="cancel", parent=self.root)
            return r 
        else: return True

        
    def help(self):
        mes="""This program is using the Mannings formula to calculate the hydraulic properties of open channels."""
        tkinter.messagebox.showinfo('Help', mes)


class TriWindow(RectWindow):

    def __init__(self, t1=45.0, t2=45.0, h=5.00, n=0.015, s=0.5, name='untitled '):
        "Initilize the window."
        self.root = tk.Toplevel(common.mainwin.root)
        common.oppened_wins.append(self)
        if name == 'untitled ':
            self.name = name + str(len(common.oppened_wins)-1)
        else:
            self.name = name
            self.filename = name.split('/')[-1]
        ico = Image.open('icon.png')
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.rownumber = 2
        self.filename = None
        self.depthmode = False
        self.statepar = [t1, t2, h, n, s] 
        self.setfonts()
        self.setmenus()
        self.makewidgets()
        self.draw(h, t1, t2)
        self.winmenuupdate()
        self.update()
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.title(self.name)
        self.initvalues(t1, t2, h, s, n)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()

    @staticmethod
    def newrec():
        RectWindow()
        
    @staticmethod
    def newtrap():
        TrapWindow()

    @staticmethod
    def newtri():
        TriWindow()

    @staticmethod
    def newcir():
        CirWindow()
    
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


    def initvalues(self, t1, t2, h, s, n):
        "Sets the initial values"
        self.entDepth.delete(0, 'end')
        self.entDepth.insert(0, str(h))
        self.entSlope.delete(0, 'end')
        self.entSlope.insert(0, str(s))
        self.entManning.delete(0, 'end')
        self.entManning.insert(0, str(n))
        self.entt1.delete(0, 'end')
        self.entt1.insert(0, str(t1))
        self.entt2.delete(0, 'end')
        self.entt2.insert(0, str(t2))

    
    def save(self):
        "Saves the file to the already loaded file."
        if self.filename == None:
            self.saveas()
        else:
            values = self.getvalues()
            if values == None: return
            self.savetofile(self.filename, values)
    
    
    def saveas(self):
        "Saves the file to a selected file."
        values = self.getvalues()
        if values == None: return
        fr = tkinter.filedialog.asksaveasfile(parent=self.root, defaultextension='.hyd', title="Select file to Save.")
        if fr == None: return #User cancelled.
        self.filename = fr.name
        self.name = self.filename
        self.root.title(self.filename)
        self.update()
        fr.close
        self.savetofile(self.filename, values)

   
    def savetofile(self, fr, values):
        "Writes to the file when called."
        t1d, t2d, h, n, s = values
        t1 = 1/math.tan(math.radians(t1d))
        t2 = 1/math.tan(math.radians(t2d))
        chan = hydro.TrapezChannel(s, n, 0, t1, t2)
        try:
            chan.write(fr, h)
            self.statepar = values
        except IOError as e:
                tkinter.messagebox.showerror('Error', str(e))
                self.saveas()
                return


    def togglemode(self):
        for ent in [self.entDepth, self.entSlope, 
                    self.entManning, self.entVel, self.entDis]:
            ent.config(state='normal')
        if self.depthmode == True:
            self.modelab.config(text='Mode: Normal')
            self.depthmode = False
        else:
            self.depthmode = True
            self.modelab.config(text='Mode: Depth')
        if self.depthmode:
            self.entDepth.config(state='readonly')
        else:
            self.entDis.config(state='readonly')
        self.entVel.config(state='readonly')
        
       
    def getvalues(self, depthmode=False, showerrors=True):
        "Gets the values from the entries"
        values = []
        t1 = self.checkvalues(self.entt1, vmin=0.0, vmax=179.0, showerrors=showerrors)
        if t1 == None:
            return
        values.append(t1)
        t2 = self.checkvalues(self.entt2, vmin=0.0, vmax=179.0, showerrors=showerrors)
        if t2 == None:
            return
        values.append(t2)
        if depthmode:
            h = self.checkvalues(self.entDis)
        else:
            h = self.checkvalues(self.entDepth, vmin=0.00, vmax=220,showerrors=showerrors)
        if h == None:
            return
        values.append(h)
        n = self.checkvalues(self.entManning, vmin=0.001, vmax=0.1, showerrors=showerrors)
        if n == None:
            return
        values.append(n)
        s = self.checkvalues(self.entSlope,  vmin=0.01, vmax=1000, showerrors=showerrors)
        if s == None:
            return
        values.append(s)
        return values
    
    
    def checkvalues(self, ent, vmin=None, vmax=None, showerrors=False):
        try: value = float(ent.get().replace(',','.'))
        except: value = None
        if showerrors:
            if value == None: 
                tkinter.messagebox.showwarning("Error", "A value is missing")
                ent.focus_set()
                return None
            if vmin is not None:
                if value < vmin:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
                elif value > vmax:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
        return value


    def setresults(self, results, depthmode=False):
        "Sets the results"
        if self.depthmode:
            ent = self.entDepth
        else:
            ent = self.entDis
        ent.config(state='normal')
        ent.delete(0, 'end')
        ent.insert(0, str(results[1]))
        ent.config(state='readonly')
        self.entVel.config(state='normal')
        self.entVel.delete(0, 'end')
        self.entVel.insert(0, str(results[0]))
        self.entVel.config(state='readonly')


    def setfonts(self):
        "Sets the font for the GUI."
        defaultfont = tkinter.font.Font(name="TkDefaultFont", exists=True)
        defaultfont.config(size=20, family='Arial')
        textfont = tkinter.font.Font(name="TkTextFont", exists=True)
        textfont.config(family="Arial", size=20)
        fixedfont = tkinter.font.Font(name="TkFixedFont", exists=True)
        fixedfont.config(size=20)
        captionfont = tkinter.font.Font(name="TkCaptionFont", exists=True)
        captionfont.config(size=14)
        menufont = tkinter.font.Font(name="TkMenuFont", exists=True)
        menufont.config(size=20)
        self.buttonfont=tkinter.font.Font(size=16, family='Arial')


    def setmenus(self):
        "Sets the menus fot the GUI."
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", menu=filemenu)
        newmenu = tk.Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='New', menu=newmenu)
        filemenu.add_command(label='Load', command=self.load)
        filemenu.add_command(label='Save', command=self.save)
        filemenu.add_command(label='Save As', command=self.saveas)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.exit)
        newmenu.add_command(label='Rectangular', command=self.newrec)
        newmenu.add_command(label='Triangular', command=self.newtri)
        newmenu.add_command(label='Trapezoidal', command=self.newtrap)
        newmenu.add_command(label='Circular', command=self.newcir)
        self.winmenuupdate()
        self.menubar.add_command(label='Help', command=self.help)
        self.root.config(menu=self.menubar)

    
    def winmenuupdate(self):
        self.windowmenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Window', menu=self.windowmenu)
        for win in common.oppened_wins:
            self.windowmenu.add_command(label=win.name, command=win.root.lift)


    def update(self):
        for win in common.oppened_wins:
            win.setmenus()


    def labentry(self, rownumber, desc, def_value=''):
        "Creates a label with an entry next to it."
        lab = tk.Label(self.root, text=desc)
        lab.grid(row=rownumber, column=0, sticky='e')
        ent = tk.Entry(self.root, width=18)
        ent.grid(row=rownumber, column=1,  sticky='we')
        ent.insert(0, def_value)
        return ent


    def makewidgets(self): 
        "Initilizes the Widgets."
        lab = tk.Label(self.root, text='School of Civil Engineering', foreground='green')
        lab.grid(row=0, column=0, columnspan=2)
        lab = tk.Label(self.root, text='Triangular', foreground='green')
        lab.grid(row=0, column=2)
        self.canvas = tk.Canvas(self.root, background='darkgrey', height=200, width=500)
        self.canvas.grid(row=1, column=0, columnspan=3, sticky='wesn')
        self.rownumber += 1 
        self.entt1 = self.labentry(self.rownumber, 'LAngle (deg):')
        self.modelab = tk.Label(self.root, text='Mode: Normal',width= 15)
        self.modelab.grid(row=self.rownumber, column=2)
        self.rownumber += 1 
        self.entt2 = self.labentry(self.rownumber, 'RAngle (deg):')
        togglebutton = tk.Button(self.root, text='Toggle', command=self.togglemode, font=self.buttonfont)
        togglebutton.grid(row=self.rownumber, column=2)
        self.rownumber += 1 
        self.entDepth = self.labentry(self.rownumber, "Depth (m):", '4.00')
        self.rownumber += 1  
        self.entSlope = self.labentry(self.rownumber, "Slope(%):", '0.5')
        self.rownumber += 1 
        self.entManning = self.labentry(self.rownumber, "Manning:", '0.015')
        self.rownumber += 1
        compute = tk.Button(self.root, text='Compute', command=self.compute, font=self.buttonfont)
        compute.grid(row=self.rownumber, column=2)
        self.entVel = self.labentry(self.rownumber, "Velocity (m/s):", '')
        self.rownumber += 1
        self.entDis = self.labentry(self.rownumber, "Discharge (m3/s):", '')
        self.entVel.config(state='readonly')
        self.entDis.config(state='readonly')

    def draw(self,h , t1, t2):
        "Draw the open channel."
        dc = self.canvas
        dc.update_idletasks() # _idletasks breaks WinDoze 98 support
        dcw = dc.winfo_width() # Pixels
        dch = dc.winfo_height() # Pixels
        if dcw < 2 or dch < 2: return #tkinter reported wrong width or height
        #perx = dcw*0.05 #Margin x
        pery = dch*0.05 #Margin y
        dcwef = dcw# - 2*perx #Effective width is now smaller
        dchef = dch - 2*pery #Effective height is now smaller
        dc.delete(tk.ALL) # Clear window
        hchan = h*1.1 #Height of channel is bigger than water level
        akl = dcwef/(2*hchan/math.tan(t1*math.pi/180))
        akly= dchef/hchan
        if akly < akl: akl = akly
        perx = dcw/2 #Margin x
        def topix(x, y): return perx+x*akl, dch-(pery+y*akl)
        cs = ((-h/math.tan(t1*math.pi/180), h), (0, 0), (h/math.tan(t2*math.pi/180), h)) #Draw water surface
        cs = [topix(x, y) for x, y in cs]
        dc.create_polygon(cs, fill="cyan", outline=None, stipple="gray25")
        cs = ((-h/math.tan(t1*math.pi/180), h), (h/math.tan(t2*math.pi/180), h)) #Draw water level
        cs = [topix(x, y) for x, y in cs]
        dc.create_line(cs, fill="blue", width=3)
        cs = ( (-hchan/math.tan(t1*math.pi/180), hchan), (0, 0), (hchan/math.tan(t2*math.pi/180), hchan)) #Draw channel
        cs = [topix(x, y) for x, y in cs]
        dc.create_line(cs, fill="brown", width=3) 

    def compute(self, depthmode=False):
        values = self.getvalues(depthmode=self.depthmode)
        if values == None: return
        t1d, t2d, h, n, s = values
        s /= 100
        t1 = 1/math.tan(math.radians(t1d))
        t2 = 1/math.tan(math.radians(t2d))
        channel = hydro.TrapezChannel(s, n, 0, t1, t2)
        if self.depthmode:
            v, q = channel.depth(h)
            self.draw(q, t1d, t2d)
        else: 
            v, q = channel.discharge(h)
            self.draw(h, t1, t2)
        self.setresults((v,q))


    def exit(self):
        if not self.ok2quit():
            return
        common.oppened_wins.remove(self)
        self.root.destroy()
        self.update()
        del self.entDepth, self.entDis, self.entt1, self.entt2
        del self.entSlope, self.entManning, self.entVel

    
    def ok2quit(self):
        if self.statepar != self.getvalues(depthmode=False, showerrors=False):
            r = tk.messagebox.askokcancel("Data is not saved",
            "ok to abandon changes?", default="cancel", parent=self.root)
            return r 
        else: return True

        
    def help(self):
        mes="""This program is using the Mannings formula to calculate the hydraulic properties of open channels."""
        tkinter.messagebox.showinfo('Help', mes)


class CirWindow(RectWindow):


    def __init__(self, d=8.00, h=5.00, n=0.015, s=0.5, name='untitled '):
        "Initilize the window."
        self.root = tk.Toplevel(common.mainwin.root)
        common.oppened_wins.append(self)
        if name == 'untitled ':
            self.name = name + str(len(common.oppened_wins)-1)
        else:
            self.name = name
            self.filename = name.split('/')[-1]
        ico = Image.open('icon.png')
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.rownumber = 2
        self.filename = None
        self.depthmode = False
        self.statepar = [d/2, h, n, s] 
        self.setfonts()
        self.setmenus()
        self.makewidgets()
        self.draw(d/2, h)
        self.winmenuupdate()
        self.update()
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.title(self.name)
        self.initvalues(h, d, s, n)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()

    @staticmethod
    def newrec():
        RectWindow()
        
    @staticmethod
    def newtrap():
        TrapWindow()

    @staticmethod
    def newtri():
        TriWindow()

    @staticmethod
    def newcir():
        CirWindow()
    
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
                tkinter.messagebox.showerror('Error', 'There has been an error loading the file'+ self.filename + ':' + str(e))
                return
        if channeltype == 'rectangular':
            RectWindow(chan.b, h, chan.n, chan.s, self.filename)
        elif channeltype == 'trapezoidal':
            TrapWindow(math.degrees(math.atan(1/chan.t1)), math.degrees(math.atan(1/chan.t2)), chan.b, h, chan.n, chan.s, self.filename)
        elif channeltype == 'triangular':
            TriWindow(math.degrees(math.atan(1/chan.t1)), math.degrees(math.atan(1/chan.t2)), h, chan.n, chan.s, self.filename)
        elif channeltype == 'circular':
            CirWindow(chan.d, h, chan.n, chan.s, self.filename)


    def initvalues(self, h, d, s, n):
        "Sets the initial values"
        self.entDepth.delete(0, 'end')
        self.entDepth.insert(0, str(h))
        self.entDiameter.delete(0, 'end')
        self.entDiameter.insert(0, str(d))
        self.entSlope.delete(0, 'end')
        self.entSlope.insert(0, str(s))
        self.entManning.delete(0, 'end')
        self.entManning.insert(0, str(n))

    
    def save(self):
        "Saves the file to the already loaded file."
        if self.filename == None:
            self.saveas()
        else:
            values = self.getvalues()
            if values == None: return
            self.savetofile(self.filename, values)
    
    
    def saveas(self):
        "Saves the file to a selected file."
        values = self.getvalues()
        if values == None: return
        fr = tkinter.filedialog.asksaveasfile(parent=self.root, defaultextension='.hyd', title="Select file to Save.")
        if fr == None: return #User cancelled.
        self.filename = fr.name
        self.name = self.filename
        self.root.title(self.filename)
        self.update()
        fr.close
        self.savetofile(self.filename, values)

   
    def savetofile(self, fr, values):
        "Writes to the file when called."
        r, h , n, s = values
        chan = hydro.CircularChannel(s, n, r)
        try:
            chan.write(fr, h)
            self.statepar = values
        except IOError as e:
                tkinter.messagebox.showerror('Error', str(e))
                self.saveas()
                return


    def togglemode(self):
        for ent in [self.entDiameter, self.entDepth, self.entSlope, 
                    self.entManning, self.entVel, self.entDis]:
            ent.config(state='normal')
        if self.depthmode == True:
            self.modelab.config(text='Mode: Normal')
            self.depthmode = False
        else:
            self.depthmode = True
            self.modelab.config(text='Mode: Depth')
        if self.depthmode:
            self.entDepth.config(state='readonly')
        else:
            self.entDis.config(state='readonly')
        self.entVel.config(state='readonly')
        
       
    def getvalues(self, depthmode=False, showerrors=True):
        "Gets the values from the entries"
        values = []
        r = self.checkvalues(self.entDiameter, vmin=0.001, vmax=10000, showerrors=showerrors)/2
        if r == None:
            return
        values.append(r)
        if depthmode:
            h = self.checkvalues(self.entDis)
        else:
            h = self.checkvalues(self.entDepth, vmin=0, vmax=r*2*0.95,showerrors=showerrors)
        if h == None:
            return
        values.append(h)
        n = self.checkvalues(self.entManning, vmin=0.001, vmax=0.1, showerrors=showerrors)
        if n == None:
            return
        values.append(n)
        s = self.checkvalues(self.entSlope,  vmin=0.01, vmax=1000, showerrors=showerrors)
        if s == None:
            return
        values.append(s)
        return values
    
    
    def checkvalues(self, ent, vmin=None, vmax=None, showerrors=False):
        try: value = float(ent.get().replace(',','.'))
        except: value = None
        if showerrors:
            if value == None: 
                tkinter.messagebox.showwarning("Error", "A value is missing")
                ent.focus_set()
                return None
            if vmin is not None:
                if value < vmin:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
                elif value > vmax:
                    tkinter.messagebox.showerror('Value out of bounds',"Value is expected to be between " + str(vmin) + ' and ' + str(vmax) + ' is found ' + str(value))
                    return
        return value


    def setresults(self, results, depthmode=False):
        "Sets the results"
        if self.depthmode:
            ent = self.entDepth
        else:
            ent = self.entDis
        ent.config(state='normal')
        ent.delete(0, 'end')
        ent.insert(0, str(results[1]))
        ent.config(state='readonly')
        self.entVel.config(state='normal')
        self.entVel.delete(0, 'end')
        self.entVel.insert(0, str(results[0]))
        self.entVel.config(state='readonly')


    def setfonts(self):
        "Sets the font for the GUI."
        defaultfont = tkinter.font.Font(name="TkDefaultFont", exists=True)
        defaultfont.config(size=20, family='Arial')
        textfont = tkinter.font.Font(name="TkTextFont", exists=True)
        textfont.config(family="Arial", size=20)
        fixedfont = tkinter.font.Font(name="TkFixedFont", exists=True)
        fixedfont.config(size=20)
        captionfont = tkinter.font.Font(name="TkCaptionFont", exists=True)
        captionfont.config(size=14)
        menufont = tkinter.font.Font(name="TkMenuFont", exists=True)
        menufont.config(size=20)
        self.buttonfont=tkinter.font.Font(size=16, family='Arial')


    def setmenus(self):
        "Sets the menus fot the GUI."
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", menu=filemenu)
        newmenu = tk.Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='New', menu=newmenu)
        filemenu.add_command(label='Load', command=self.load)
        filemenu.add_command(label='Save', command=self.save)
        filemenu.add_command(label='Save As', command=self.saveas)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.exit)
        newmenu.add_command(label='Rectangular', command=self.newrec)
        newmenu.add_command(label='Triangular', command=self.newtri)
        newmenu.add_command(label='Trapezoidal', command=self.newtrap)
        newmenu.add_command(label='Circular', command=self.newcir)
        self.winmenuupdate()
        self.menubar.add_command(label='Help', command=self.help)
        self.root.config(menu=self.menubar)

    
    def winmenuupdate(self):
        self.windowmenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Window', menu=self.windowmenu)
        for win in common.oppened_wins:
            self.windowmenu.add_command(label=win.name, command=win.root.lift)


    def update(self):
        for win in common.oppened_wins:
            win.setmenus()


    def labentry(self, rownumber, desc, def_value=''):
        "Creates a label with an entry next to it."
        lab = tk.Label(self.root, text=desc)
        lab.grid(row=rownumber, column=0, sticky='e')
        ent = tk.Entry(self.root, width=18)
        ent.grid(row=rownumber, column=1,  sticky='we')
        ent.insert(0, def_value)
        return ent


    def makewidgets(self):
        "Initilizes the Widgets."
        lab = tk.Label(self.root, text='School of Civil Engineering', foreground='green')
        lab.grid(row=0, column=0, columnspan=2)
        lab = tk.Label(self.root, text='Circular', foreground='green')
        lab.grid(row=0, column=2)
        self.canvas = tk.Canvas(self.root, background='darkgrey', height=200, width=500)
        self.canvas.grid(row=1, column=0, columnspan=3, sticky='wesn')
        self.rownumber += 1 
        self.entDiameter = self.labentry(self.rownumber, "Diameter (m):", '8.00')
        self.modelab = tk.Label(self.root, text='Mode: Normal',width= 15)
        self.modelab.grid(row=self.rownumber, column=2)
        self.rownumber += 1  
        togglebutton = tk.Button(self.root, text='Toggle', command=self.togglemode, font=self.buttonfont)
        togglebutton.grid(row=self.rownumber, column=2)
        self.entDepth = self.labentry(self.rownumber, "Depth (m):", '5.00')
        self.rownumber += 1 
        self.entSlope = self.labentry(self.rownumber, "Slope(%):", '0.5')
        self.rownumber += 1 
        self.entManning = self.labentry(self.rownumber, "Manning:", '0.015')
        self.rownumber += 1
        compute = tk.Button(self.root, text='Compute', command=self.compute, font=self.buttonfont)
        compute.grid(row=self.rownumber, column=2)
        self.entVel = self.labentry(self.rownumber, "Velocity (m/s):", '')
        self.rownumber += 1
        self.entDis = self.labentry(self.rownumber, "Discharge (m3/s):", '')
        self.entVel.config(state='readonly')
        self.entDis.config(state='readonly')

    def draw(self, r, h):
        "Draw the open channel."
        dc = self.canvas
        dc.update_idletasks() # _idletasks breaks WinDoze 98 support
        dcw = dc.winfo_width() # Pixels
        dch = dc.winfo_height() # Pixels
        if dcw < 2 or dch < 2: return #tkinter reported wrong width or height
        #perx = dcw*0.05 #Margin x
        pery = dch*0.05 #Margin y
        dcwef = dcw# - 2*perx #Effective width is now smaller
        dchef = dch - 2*pery #Effective height is now smaller
        dc.delete(tk.ALL) # Clear window
        hchan = 2*r
        rchan = 2*r
        akl = dcwef/rchan
        akly= dchef/hchan
        if akly < akl: akl = akly
        perx = dcw/2 - akl*(r) #Margin x
        def topix(x, y): return perx+x*akl, dch-(pery+y*akl)
        cs = ( (2*r,0) , (0,2*r)) #Draw channel
        cs = [topix(x, y) for x, y in cs]
        dc.create_oval(cs, width=3, fill='cyan', outline='brown', stipple='gray25')
        cs = ( (-10*r, h), (10*r, 10*h) ) 
        cs = [topix(x, y) for x, y in cs]
        dc.create_rectangle(cs, fill="darkgrey", outline=None, width=0)


    def compute(self, depthmode=False):
        values = self.getvalues(depthmode=self.depthmode)
        if values == None: return
        r ,h, n, s = values
        s /= 100
        channel = hydro.CircularChannel(s, n, r)
        if self.depthmode:
            v, q = channel.depth(h)
            self.draw(r, q)
        else:  
            v, q = channel.discharge(h)
            self.draw(r, h)
        if v == -1 or q == -1  or h == -1:
            tkinter.messagebox.showerror('Hydro Error', 'Discharge is too large for this diameter of channel')
        self.setresults((v,q))


    def exit(self):
        if not self.ok2quit():
            return
        common.oppened_wins.remove(self)
        self.root.destroy()
        self.update()
        del self.entDiameter, self.entDepth, self.entDis
        del self.entSlope, self.entManning, self.entVel

    
    def ok2quit(self):
        if self.statepar != self.getvalues(depthmode=False, showerrors=False):
            r = tk.messagebox.askokcancel("Data is not saved",
            "ok to abandon changes?", default="cancel", parent=self.root)
            return r 
        else: return True

        
    def help(self):
        mes="""This program is using the Mannings formula to calculate the hydraulic properties of open channels."""
        tkinter.messagebox.showinfo('Help', mes)

