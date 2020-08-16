from  flask_main import *
import connectionManager
import multiprocessing

def start_flask():
    host = 'localhost'
    port = 5050
    print(f'-- Flask is started on {host}:{port}')
    app.run('localhost', 5050)

def main():
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=connectionManager.init, args=(queue, "localhost", 5757))
    proc.start()

    flask_init(queue)
    start_flask()

if __name__ == "__main__":
    main()