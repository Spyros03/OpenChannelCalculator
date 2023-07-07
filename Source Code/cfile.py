
class CFile:

    def __init__(self, fn):
        "Initializes the object variables."
        self.fn = fn
        self.iline = 0
        self.fr = open(fn, 'r')
       

    def getline(self, failoneof=True):
        "Reads and returns the next line of the file, ignoring comments and blanck lines"
        while True:
            dline = self.fr.readline()
            if dline == '':
                if failoneof == True:
                    self.ereof()
                if failoneof == False:
                    return None
            self.iline += 1
            dline = dline.split('#')[0]
            if dline.strip() != '':
                return dline
        
        
    def ereof(self, mes=""):
        "Raises exception with rich error message"
        errmessage = "Unexpected end of file {} after line {}\n".format(self.fn, self.iline) + mes
        raise IOError(errmessage)
    

    def er(self, mes):
        "Raises exception with rich error message"
        errmessage = "Error at line {} of file {}:\n".format(self.iline, self.fn) + mes
        raise ValueError(errmessage)
    

    def getlabel(self, lab, failoneof=True):
        "Ensures that label exists on the next line of file."
        dline = self.getline(False)
        if dline == None:
            if failoneof == True:
                mes = "Expected label '{}'".format(lab)
                self.ereof(mes)
            else:
                failoneof == False
                return None
        dline = dline.split(":")
        if lab.lower() == dline[0].strip().lower():
            summline = ''
            for line in dline[1::]:
                summline += line 
            return summline.strip()
        else:
            mes = "Expected label '{}', found '{}'".format(lab, dline[0].strip())
            self.er(mes)


    def getreals(self, lab, n, vmin=None, vmax=None):
        "Reads n reals after label form the next line of the file."
        reals = []
        dline = self.getlabel(lab)
        nums = dline.split()
        for i in range(len(nums)):
            try:
                reals.append(float(nums[i].strip()))
            except ValueError:
                continue
        if len(reals) != n:
            mes = "Expected {} real numbers".format(n)
            self.er(mes)
        if vmin != None:
            for real in reals:
                if real < vmin:
                    mes = "Expected real numbers >= {}, found {}".format(vmin, real)
                    self.er(mes)
        if vmax != None:
            for real in reals:
                if real > vmax:
                    mes = "Expected real numbers <= {}, found {}".format(vmax, real)
                    self.er(mes)
        return tuple(reals)

        
    def getchoice(self, lab, choices):
        "Reads one of allowed choices after the label form the next line of file."
        dline = self.getlabel(lab).strip()
        for i in range(len(choices)):
            if dline.lower() == choices[i].lower():
                return choices[i]
        else:
            sumchoice = choices[0]
            for choice in choices[1::]:
                sumchoice += ',' + choice    
            mes = "Expected one of '{}', found '{}'".format(sumchoice, dline)
            self.er(mes)

        
    def close(self):
        "Closes the file object."
        self.fr.close()

