import requests
import sys
import http.client

## make this boi a big ol' class

class client():

    def __init__(self, ip, port):
        self.ip = '127.0.0.1'
        self.port = 8000
        self.httpMsg = 'http://'
        self.clientIden = -1 #default for disconnected
        self.r = ""

        if(str(ip) != str(-1)):
            self.ip = ip

        if(int(port) != -1):
            port = int(port)

        self.httpMsg = self.httpMsg + str(self.ip) + ':' + str(self.port)
        self.getInit()

        print("\nConnecting to server @" + str(self.httpMsg))
        self.ui()
        print("\nClosing client...")

        

    def ui(self):
        choice = 0
        while(choice != 5):
            self.menu()
            choice = int(input("Enter your choice: "))
            if (choice == 1):
                self.play()
            elif (choice == 2):
                self.get("results")
            elif (choice == 3):
                self.get("score")
            elif (choice == 4):
                self.reset()
            elif (choice != 5):
                print("That is not a valid option.  Please try again.")



    def menu(self):
        print()
        print("1. Make a play.")
        print("2. Check results.")
        print("3. Check score.")
        print("4. Request reset.")
        print("5. Quit.")



    def optionsMenu(self):
        print()
        print("1. Rock")
        print("2. Paper")
        print("3. Scizors")
        print("4. Back")


        
    def play(self):
        choice = 0
        while(choice != 4):
            self.optionsMenu()
            choice = int(input("Enter your choice: "))
            if (choice == 1):
                self.put(False, "rock")
                choice = 4
            elif (choice == 2):
                self.put(False, "paper")
                choice = 4
            elif (choice == 3):
                self.put(False, "scizors")
                choice = 4
            elif (choice != 4):
                print("That is not a valid option.  Please try again.")



    def reset(self):
        self.put(True, None)



    def getInit(self):
        self.r = self.get('init')
        if(self.r.status_code != 200):
            print("\nExiting...")
            exit()
        self.clientIden = int(self.r.text)



    def get(self, data):
        self.r = requests.get(self.httpMsg, {'type': str(data), 'iden' : str(self.clientIden)})
        if(int(self.r.status_code) == 200):
            print("\n", self.r.status_code, self.r.reason, self.r.text)
        else:
            print("\n", self.r.status_code, self.r.reason)
        return self.r



    def put(self, reset, play):
        data = {'reset': str(reset), 'play': str(play), 'iden' : str(self.clientIden)}
        self.r = requests.put(self.httpMsg, data)
        
        if(int(self.r.status_code) == 200):
            print("\n", self.r.status_code, self.r.reason, self.r.text)
        else:
            print("\n", self.r.status_code, self.r.reason)
        return self.r
    

#Send message to server (make a play)

#Check results and display

#Check game score and display... treat a game as a resource


def run():
    if(len(sys.argv) == 3):
        ip = sys.args[1]
        port = int(sys.args[2])
        c = client(ip, port)
    else:
        c = client("-1", -1)


if __name__ == "__main__":
    run()


