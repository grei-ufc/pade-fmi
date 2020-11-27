from typing import Callable
from twisted.internet import reactor

from pade.core.agent import Agent
from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage


class FmiAdapter(Behaviour):
    """
        The FMI adapter is a behaviour that makes is possible for agents 
        to communicate with FMI Wrappers.
    """

    def __init__(self, agent: Agent, on_request: Callable[[ACLMessage], None]):
        self.agent = agent
        self.on_request = on_request
        self.wrapper_name = 'fmi-wrapper'

    def execute(self, message: ACLMessage):
        """Executed when the agent receives any message"""
        if message.sender.localname == self.wrapper_name:
            self.on_request(message)

    def send_inform(self, message: ACLMessage):
        """Use low-level twisted method to send message"""
        receiver = message.receivers[0]
        try:
            self.agent.agentInstance.messages.append((receiver, message))
            reactor.connectTCP(receiver.host, receiver.port,
                               self.agent.agentInstance)
        except:
            self.agent.agentInstance.messages.pop()
