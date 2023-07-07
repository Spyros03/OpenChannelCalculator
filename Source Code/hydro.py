import util
import cfile
import math




class Channel:


    cname = "channel"


    def __init__(self, s, n):
        "Initialize the object variables."
        self.s = s
        self.n = n
        self.hmax = 220

    
    def perarea(self, h):
        "Computes wetted perimeter and area of wet section of channel."
        if h < 0 or h > self.hmax:
            p = a = -1
            return p, a
        assert False, "method perarea() must be overwritten"
        

    
    def discharge(self, h):
        "Computes mean velocity and discharge of channel."
        if h < 0 or h > self.hmax:
            v = q = -1
            return v, q
        p, a = self.perarea(h)
        if h == 0:Rh = 0
        else:
            Rh = a/p
        v = (1/self.n)*Rh**(2/3)*self.s**(1/2)
        q = v * a
        return v, q

    
    def depth(self, q):
        "Computes mean velocity and depth of channel."
        vmax, qmax = self.discharge(self.hmax)
        if q < 0 or q > qmax:
            v = h = -1
            return v, h
        try:
            def f(x):
                temp, Q = self.discharge(x)
                return Q - q
            h = util.bisecroot(f ,0, self.hmax, 1e-4)
            v, temp = self.discharge(h)
        except AssertionError:
            v = h =-2
        
        return v, h
    

    @staticmethod
    def read(fn):
        "Reads channel attributes from a file."
        file = cfile.CFile(fn)
        channeltype = file.getchoice('Type',('rectangular', 'trapezoidal', 'triangular', 'circular'))
        temp = file.getreals('Slope', 1, vmin = 0.01, vmax = 1000)
        s = temp[0]/100
        temp = file.getreals('Manning', 1, vmin = 0.001, vmax = 0.1)
        n = temp[0]
        temp = file.getreals('depth', 1, vmin = 0, vmax = 220)
        h = temp[0]
        if channeltype == 'rectangular':
            chan = RectChannel(s,n)
            chan.read2(file)
        elif channeltype == 'trapezoidal':
            chan = TrapezChannel(s,n)
            chan.read2(file)
        if channeltype == 'triangular':
            chan = TrapezChannel(s, n, b=0)
            chan.read2(file)
        elif channeltype == 'circular':
            chan = CircularChannel(s,n)
            chan.read2(file)  
        if h > chan.hmax:
            chan.hmax = h
        file.close()
        return channeltype, chan, h
    

    def write(self, fn, h):
        "Writes channel specific attributes to a channel."
        file = open(fn, 'w')
        file.write("Type:    {}\n".format(self.cname))
        file.write("Slope:   {}  # %\n".format(self.s*100))
        file.write('Manning: {}\n'.format(self.n))
        file.write('depth:   {}  # m\n'.format(h))
        self.write2(file)
        file.close

       
class RectChannel(Channel):


    cname = "rectangular"


    def __init__(self, s = 0.005, n = 0.015, b = 4.00):
        "Initialize the object variables."
        super().__init__(s, n)
        self.b = b


    def perarea(self, h):
        "Computes wetted perimeter and area of wet section of rectangular channel."
        p = self.b + 2*h
        a = self.b*h
        return p, a
    
    
    def read2(self, file):
        "Reads specific attributes of a channel"
        temp = file.getreals('Bottom Width', 1, vmin = 0.001, vmax =10000)
        self.b = temp[0]
    

    def write2(self, file):
        file.write('Bottom Width: {}    # m\n'.format(self.b))
        

class TrapezChannel(Channel):


    cname = "trapezoidal"


    def __init__(self, s = 0.005, n = 0.015, b = 4.00, t1 = 1.00 , t2 = 1.00):
        "Initialize the object variables."
        super().__init__(s, n)
        self.b = b
        if b == 0:
            self.cname = 'triangular'
        self.t1 = t1
        self.t2 = t2
    

    def perarea(self, h):
        "Computes wetted perimeter and area of wet section of trapezoidal channel."
        l1 = (h**2 + (h*self.t1)**2)**(1/2)
        l2 = (h**2 + (h*self.t2)**2)**(1/2)
        p = l1 + l2 + self.b
        a = h**2*(self.t1+self.t2)/2 + self.b*h
        return p, a
    

    def read2(self, file):
        "Reads specific attributes of a channel"
        if self.b != 0:
            temp = file.getreals('Bottom Width', 1, vmin = 0.001, vmax =10000)
            self.b = temp[0]
        temp = file.getreals('Bank Angles', 2, vmin = 1, vmax = 179.0)
        self.t1 = 1/math.tan(math.radians(temp[0]))
        self.t2 = 1/math.tan(math.radians(temp[1]))



    def write2(self, file):
        if self.b != 0:
            file.write('Bottom Width: {}    # m\n'.format(self.b))
        bankanlge1 = math.degrees(math.atan(1/self.t1))
        bankanlge2 = math.degrees(math.atan(1/self.t2))
        file.write('Bank Angles:  {} {}    # deg\n'.format(bankanlge1, bankanlge2))


class CircularChannel(Channel):

    cname = 'circular'


    def __init__(self, s = 0.005, n = 0.015, r=4.00):
        super().__init__(s, n)
        self.r = r
        self.d = 2*r
        self.hmax = 2*self.r*0.95 #In order to have the required open channel to use.

    def perarea(self, h):
        "Calculates wetted perimeter and area of a circular channel."
        if h <= self.r:
            phi = math.acos((self.r-h)/self.r)
            theta = 2*phi
            p = theta*self.r
            a = phi*self.r**2 - math.tan(phi)*(self.r-h)**2
        else:
            phi = math.acos((2*self.r-h)/self.r)
            theta = 2*phi
            p = 2*math.pi*self.r - theta*self.r
            a = math.pi*self.r**2 - (phi*self.r**2 - self.r*math.tan(phi)*(self.r-h)**2)
        return p, a
    
    def read2(self, file):
        temp = file.getreals('Diameter', 1, vmin = 0.001, vmax =10000)
        self.d = temp[0]
        self.r = temp[0]/2

    
    def write2(self, file):
         file.write('Diameter: {}    # m\n'.format(self.d))


def rectPA(b, h):
    "Computes wetted perimeter and area of wet section of rectangular channel."
    P = b + 2*h
    A = b*h
    return P, A


def rectDischarge(s, n, b, h):
    "Computes mean velocity and discharge of rectangular channel."
    P, A = rectPA(b, h)
    V = 1/n*(A/P)**(2/3)*s**(1/2)
    Q = V*A
    return V, Q


def trigPA(t1, t2, h):
    "Computes wetted perimeter and area of wet section of triangular channel."
    l1 = (h**2 + (h*t1)**2)**(1/2)
    l2 = (h**2 + (h*t2)**2)**(1/2)
    P = l1 + l2
    A = h**2*(t1+t2)/2
    return P, A


def triDischarge(s, n, t1, t2, h):
    "Computes mean velocity and discharge of triangular channel."
    P, A = trigPA(t1, t2, h)
    V = 1/n*(A/P)**(2/3)*s**(1/2)
    Q = V*A
    return V, Q


def triDepth(s, n, t1, t2, Q):
    "Computes mean velocity and depth of triangular channel."
    h = (Q*n)**(3/8)*((1+t1**2)**(1/2)+(1+t2**2)**(1/2))**(2/8)*2**(5/8)/((t1+t2)**(5/8)*s**(3/16))
    V, temp = triDischarge(s, n, t1, t2, h)
    return V, h


def trapezPA(b, t1, t2, h):
    "Computes wetted perimeter and area of wet section of trapezoidal channel."
    l1 = (h**2 + (h*t1)**2)**(1/2)
    l2 = (h**2 + (h*t2)**2)**(1/2)
    P = l1 + l2 + b
    A = h**2*(t1+t2)/2 + b*h
    return P, A


def trapezDischarge(s, n, b, t1, t2, h):
    "Computes mean velocity and discharge of trapezoidal channel"
    P, A = trapezPA(b, t1, t2, h)
    V = 1/n*(A/P)**(2/3)*s**(1/2)
    Q = V*A
    return V, Q


def rectDepth(s ,n ,b, Q):
    "Computes mean veloctiy and depth of rectangular channel."
    def f(h):
        P, A = rectPA(b, h)
        V = 1/n*(A/P)**(2/3)*s**(1/2)
        return V*A - Q
    h = util.bisecroot(f, 0, 100, 0.0001)
    V, temp = rectDischarge(s, n, b, h)
    return V, h


def trapezDepth(s, n, b, t1, t2, Q):
    "Computes mean velocity and depth of trapezodial channel."
    def f(h):
        P, A = trapezPA(b, t1, t2, h)
        V = 1/n*(A/P)**(2/3)*s**(1/2)
        return V*A - Q
    h = util.bisecroot(f, 0, 100, 0.0001)
    V, temp = trapezDischarge(s, n, b, t1, t2, h)
    return V, h