import time
from queue import Queue

from pade_fmi.fmi_wrapper import Server


def test_server():
    queue = Queue()
    server = Server(queue)
    print(server.get_address())
    server.start()
    server.terminate()
    server.join()


if __name__ == "__main__":
    test_server()
