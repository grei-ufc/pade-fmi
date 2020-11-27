import json
import logging
import os
import socket
import time
from multiprocessing import Process
from pprint import pprint
from queue import Empty, Queue
from threading import Thread
from uuid import uuid1

import matplotlib.pyplot as plt
import numpy
import pade_fmi
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pade.misc.utility import display_message
from pade_fmi import FmiAdapter, PadeSlave
from pyfmi import load_fmu

from conftest import start_loop_test

logging.basicConfig(filename='pade-fmi.log', level=logging.DEBUG)


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


def test_padefmi(start_runtime):

    # Start PyFMI thread that waits for agent
    def pade():

        agent = FMIAgent(AID('agent@localhost:55555'))
        agent.ams = ams_dict

        start_loop([agent])

    p = Process(target=pade)
    p.start()

    model = load_fmu(f'{os.path.dirname(__file__)}/{PadeSlave.__name__}.fmu')
    inputs = ('input', lambda t: 5. * numpy.cos(t))
    res = model.simulate(final_time=30, input=inputs)
    plt.plot(res['time'], res['input'])
    plt.plot(res['time'], res['output'])
    plt.xlabel('time')
    plt.show()

