from  flask_main import *
import connectionManager
import multiprocessing

def main():
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=connectionManager.init, args=(queue, "localhost", 5757))
    proc.start()

    flask_init(queue)

if __name__ == "__main__":
    main()
    app.run('localhost', 5050)