class test():
    def __init__(self):
        self.data = "fasdjsnjg"

    def getter(self):
        return self.data

def getData(testObject):
    return testObject.getter()

def main():
    t = test()
    print(getData(t))
    print(t.getter())
    print(t.data)

    def getTest():
        return t
    
    
main()
print(getTest().getter())
