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


class PadeSlave(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logging.info('Fmi2Slave.__init__')

        self.load_config()
        self._prepare_comms()

    def load_config(self):
        logging.info('load_info')
        logging.debug(__file__)
        try:
            with open(os.path.dirname(__file__) + '/fmu.json') as file:
                config = json.load(file)
        except Exception as e:
            logging.critical('File not found')
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

    def _prepare_comms(self):
        self.queue = Queue()

        def receiving():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('localhost', 0))
            server.listen(1)

            self.wrapper_aid = AID(
                f"{self.wrapper_name}@{':'.join(map(str, server.getsockname()))}"
            )

            while True:
                conn, addr = server.accept()
                logging.debug(f'New connection from {(conn, addr)}')

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    # Message received
                    message = pickle.loads(data)
                    self.queue.put(message)

                conn.close()

        self.thread = Thread(target=receiving)

    def get_agent_response(self, **kwargs):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                client.connect((self.agent_aid.host, self.agent_aid.port))
            except ConnectionRefusedError:
                pass
            else:
                logging.info(f'Connected to agent {self.agent_aid.name}')
                break

        content = {
            var.name: var.getter()
            for var in self.vars.values()
            if var.causality == pade_fmi.Fmi2Causality.input}
        content.update(kwargs)

        message = ACLMessage(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.set_performative(ACLMessage.REQUEST)
        message.set_sender(self.wrapper_aid)
        message.add_receiver(self.agent_aid)
        message.set_message_id()
        message.set_conversation_id(str(uuid1()))
        message.set_content(json.dumps(content))
        message.set_datetime_now()

        client.send(pickle.dumps(message))
        client.close()

        return self.queue.get()

    def setup_experiment(self, start_time):
        logging.info('setup_experiment')
        self.thread.start()

    def enter_initialization_mode(self):
        logging.info('enter_initialization_mode')

    def exit_initialization_mode(self):
        logging.info('exit_initialization_mode')

    def do_step(self, current_time, step_size):
        logging.info(f'do_step {current_time, step_size}')
        # Get all variables
        message = self.get_agent_response(
            current_time=current_time,
            step_size=step_size
        )
        response = json.loads(message.content)

        for key, value in response.items():
            setattr(self, key, value)

        return True
