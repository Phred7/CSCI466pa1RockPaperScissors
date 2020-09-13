import requests
import sys
import http.client

## make this boi a big ol' class

def run():

    print("\nConnecting to server @")

    ip = '127.0.0.1'
    port = 8000
    httpMsg = 'http://'

    if(len(sys.argv) == 3):
        ip = sys.argv[1]
        port = int(sys.argv[2])

    httpMsg = httpMsg + str(ip) + ':' + str(port)

    clientIden = getInit(httpMsg)
    
    print(httpMsg)
    choice = 0
    while(choice != 5):
        menu()
        choice = int(input("Enter your choice: "))
        if (choice == 1):
            play(httpMsg)
        elif (choice == 2):
            get(httpMsg, "results")
        elif (choice == 3):
            get(httpMsg, "score")
        elif (choice == 4):
            reset(httpMsg)
        elif (choice != 5):
            print("That is not a valid option.  Please try again.")

    print("\nClosing client...")
        

def menu():
    print()
    print("1. Make a play.")
    print("2. Check results.")
    print("3. Check score.")
    print("4. Request reset.")
    print("5. Quit.")

def optionsPlay():
    print()
    print("1. Rock")
    print("2. Paper")
    print("3. Scizors")
    print("4. Back")

def play(httpMsg):
    choice = 0
    while(choice != 4):
        optionsPlay()
        choice = int(input("Enter your choice: "))
        if (choice == 1):
            put(httpMsg, False, "rock")
            choice = 4
        elif (choice == 2):
            put(httpMsg, False, "paper")
            choice = 4
        elif (choice == 3):
            put(httpMsg, False, "scizors")
            choice = 4
        elif (choice != 4):
            print("That is not a valid option.  Please try again.")

def reset(httpMsg):
    put(httpMsg, True, None)

def getInit(msg):
    r = requests.get(msg, {'type': 'init'})
    print(r.text)
    #iden = int(r.text)
    return iden

def get(msg, data):
    r = requests.get(msg, {'type': str(data)})
    if(int(r.status_code) == 200):
        print("\n", r.status_code, r.reason, r.text)
    else:
        print("\n", r.status_code, r.reason)
    return r

def put(msg, reset, play):
    data = {'reset': str(reset), 'play': str(play)}
    r = requests.put(msg, data)
    
    if(int(r.status_code) == 200):
        print("\n", r.status_code, r.reason, r.text)
    else:
        print("\n", r.status_code, r.reason)


if __name__ == "__main__":
    run()
    

#Send message to server (make a play)

#Check results and display

#Check game score and display... treat a game as a resource

#Reset game

