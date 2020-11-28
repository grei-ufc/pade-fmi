import json
import logging
import os
import pickle
import socket
import time
from queue import Queue
from threading import Thread
from uuid import uuid1

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pythonfmu.fmi2slave import Fmi2Slave

import pade_fmi

logging.basicConfig(filename='pade-fmi.log', level=logging.DEBUG)


class SimulationTerminated(Exception):
    """Indicate end of simulation"""


class Client:
    def __init__(self, server_address):
        self.server_address = server_address

    def send(self, message):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.server_address)
        client.send(message)
        client.close()


class Server(Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.socket = self.open_socket()
        self.is_active = True
        self.start()

    def open_socket(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 0))
        server.setblocking(0)
        server.listen(1)
        return server

    def get_address(self):
        return self.socket.getsockname()

    def terminate(self):
        self.is_active = False

    def run(self):

        while self.is_active:
            try:
                conn, addr = self.socket.accept()
                logging.debug(f'New connection from {(conn, addr)}')

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    # Message received
                    self.queue.put(data)
                conn.close()

            except BlockingIOError:
                pass


class MessageHandler:
    @staticmethod
    def create_message(slave, params):
        content = {
            var.name: var.getter()
            for var in slave.vars.values()
            if var.causality == pade_fmi.Fmi2Causality.input
        }
        content.update(params)

        message = ACLMessage(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.set_performative(ACLMessage.REQUEST)
        message.set_sender(slave.wrapper_aid)
        message.add_receiver(slave.agent_aid)
        message.set_message_id()
        message.set_conversation_id(str(uuid1()))
        message.set_content(json.dumps(content))
        message.set_datetime_now()

        return pickle.dumps(message)

    @staticmethod
    def read_message(data):
        message = pickle.loads(data)
        return json.loads(message.content)


class PadeSlave(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logging.info('PadeSlave.__init__')

        self.load_config()

    def load_config(self):
        try:
            with open(os.path.dirname(__file__) + '/fmu.json') as file:
                config = json.load(file)
        except Exception as e:
            logging.critical('PadeSlave.File not found')
            raise e

        if 'modelInfo' in config:
            for (opt, val) in config['modelInfo'].items():
                setattr(PadeSlave, opt, val)

        self.wrapper_name = config['wrapperName']
        self.agent_aid = AID(config['agent'])

        for var in config['variables']:
            setattr(self, var['name'], var['start'])
            params = {
                'name': var['name'],
                'description': var.get('description', None),
                'causality': getattr(pade_fmi.Fmi2Causality, var['causality']) if 'causality' in var else None,
                'variability': getattr(pade_fmi.Fmi2Variability, var['variability']) if 'variability' in var else None,
                'initial': getattr(pade_fmi.Fmi2Initial, var['initial']) if 'initial' in var else None
            }
            var_type = getattr(pade_fmi, var['type'].title())
            var_instance = var_type(**params)
            self.register_variable(var_instance)

    def wait_for_event(self):
        logging.info('PadeSlave.wait_for_event')

        data = self.events_queue.get()

        if data == b'terminate':
            self.server.terminate()
            raise SimulationTerminated

        return data

    def send_message(self, **params):
        """Send message to agent."""
        logging.info('PadeSlave.send_message')
        message = MessageHandler.create_message(self, params)

        self.client.send(message)

    def setup_experiment(self, start_time):
        logging.info('PadeSlave.setup_experiment')
        self.events_queue = Queue()

        self.client = Client((self.agent_aid.host, self.agent_aid.port))
        self.server = Server(self.events_queue)
        self.wrapper_aid = AID(
            f"{self.wrapper_name}@{':'.join(map(str, self.server.get_address()))}"
        )

    def enter_initialization_mode(self):
        logging.info('PadeSlave.enter_initialization_mode')

    def exit_initialization_mode(self):
        logging.info('PadeSlave.exit_initialization_mode')

    def do_step(self, current_time, step_size):
        logging.info(f'PadeSlave.do_step {current_time, step_size}')

        # Send message and wait for response
        self.send_message(
            current_time=current_time,
            step_size=step_size
        )

        try:
            response = self.wait_for_event()
            for var, value in MessageHandler.read_message(response).items():
                setattr(self, var, value)
        except SimulationTerminated:
            pass

        return True

    def terminate(self):
        logging.info('PadeSlave.terminate')
        self.events_queue.put(b'terminate')
