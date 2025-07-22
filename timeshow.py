import datetime

def show():
    t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(t)

if __name__ == "__main__":
    show()