import pytest
import multiprocessing
import subprocess
import time
from random import randint

from pade.core import new_ams
from pade.core.sniffer import Sniffer
from pade.misc.utility import start_loop


class start_loop_test:
    """
        Start and stops reactor thread for agents under test
    """

    def __init__(self, agents):
        self.agents = agents

    def __enter__(self):
        self.p = multiprocessing.Process(
            target=start_loop, args=(self.agents,))
        self.p.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.p.terminate()


@pytest.fixture(scope='session')
def start_runtime():
    """
        Starts AMS (no sniffer) and returns its access poitnt
    """

    processes = []
    ams_dict = {'name': 'localhost', 'port': randint(9000, 60000)}

    # Start AMS in a subprocess
    commands = ['python', new_ams.__file__, 'pade_user',
                'email@', '12345', str(ams_dict['port'])]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)
    processes.append(p)

    # Delay before tests to start AMS
    time.sleep(5.0)

    # Start tests
    yield ams_dict

    # Terminate runtime
    for p in processes:
        p.terminate()
