from math import log2, sin, exp, ceil




def bisecroot(f, a, b, eps):
    "finds the root of a function using the bisection method"
    assert eps > 0, "accuracy boundary must be a positive number"
    assert a < b, "upper bound has to be larger than least bound"
    n = ceil(log2((b-a)/eps))
    if (f(a)*f(b)) > 0:
        return None
    else:
        for i in range(min((n, 30))):
            x = a + (b-a)/2
            if f(x) == 0:
                break
            elif (f(a)*f(x))<= 0:
                b = x
            else:
                a = x
    return x


if __name__ == '__main__':
    def f(x):
        return exp(x) + sin(x) - 2

    def g(msd):
        return 0.84*(1-(1-2.4*msd)**(1/2)) - 0.10
    
    def h(msd):
        return 0.84*(1-(1-2.4*msd)**(1/2)) - 0.20

    def main():
        parameters = [(f, 0, 3, 1e-4), (g, 0, 0.35, 1e-4), (h, 0, 0.35, 1e-4)]

        for parameter in parameters:
            x = bisecroot(*parameter)
            print(x)

    main()
