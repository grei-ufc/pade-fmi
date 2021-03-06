import time
from queue import Queue

from pade.fmi.fmi_wrapper import Server


def test_server():
    queue = Queue()
    server = Server(queue)
    print(server.get_address())
    server.terminate()
    server.join()


if __name__ == "__main__":
    test_server()
