from  flask_main import *
import connectionManager
import multiprocessing
from util import create_logger
    
def main():
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=connectionManager.init, args=(queue, "localhost", 5757))
    proc.start()

    create_logger()
    flask_init(queue)
    start_flask()

if __name__ == "__main__":
    main()