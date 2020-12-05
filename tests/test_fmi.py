import json
import os
import pytest
import time
from multiprocessing import Process
from pprint import pprint
from threading import Thread
from uuid import uuid1

import matplotlib.pyplot as plt
import numpy
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pade.misc.utility import display_message
from pade.fmi import FmiAdapter, PadeSlave
from pyfmi import load_fmu

from conftest import start_loop_test


class FMIAgent(Agent):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        self.fmi_adapter = FmiAdapter(self, self.on_message)
        self.behaviours.append(self.fmi_adapter)

    def on_message(self, message: ACLMessage):
        display_message(self.aid.name, f'Received message: {message.content}')
        content = json.loads(message.content)
        pprint(content)

        reply = message.create_reply()
        reply.set_content(json.dumps({
            'output': str(content['input'] * 2 + 2*content['current_time'])
        }))
        self.fmi_adapter.send_inform(reply)


@pytest.fixture(scope='module')
def fmu_generate():
    # Generate FMU from .json
    this_folder = os.path.dirname(__file__)
    fmu_json = os.path.join(this_folder, 'fmu.json')
    fmu_file = os.path.join(this_folder, f'{PadeSlave.__name__}.fmu')

    os.system(f'pade-fmi {fmu_json} -d {this_folder}')

    yield fmu_file

    # Remove FMU file after tests
    os.system(f'rm {fmu_file}')


def test_padefmi(start_runtime, fmu_generate):

    ams_dict = start_runtime

    # Start PyFMI thread that waits for agent
    def pade():
        agent = FMIAgent(AID('agent@localhost:55555'))
        agent.ams = ams_dict

        with start_loop_test([agent]):
            time.sleep(10)
    p = Process(target=pade)
    p.start()

    model = load_fmu(fmu_generate)
    inputs = ('input', lambda t: 5. * numpy.cos(t))
    res = model.simulate(final_time=30, input=inputs)
    plt.plot(res['time'], res['input'])
    plt.plot(res['time'], res['output'])
    plt.legend(['input', 'output'])
    plt.xlabel('time')
    plt.show()
