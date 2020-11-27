import json

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop
from pade_fmi import FmiAdapter


class FMIAgent(Agent):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        self.fmi_adapter = FmiAdapter(self, self.on_message)
        self.behaviours.append(self.fmi_adapter)

    def on_message(self, message: ACLMessage):
        content = json.loads(message.content)
        display_message(self.aid.name, content)

        reply = message.create_reply()
        reply.set_content(json.dumps({
            'outputVariable': content['inputVariable'] * 2 + 2*content['current_time']
        }))
        self.fmi_adapter.send_inform(reply)

if __name__ == "__main__":
    agent = FMIAgent(AID('fmi-agent@localhost:12345'))

    start_loop([agent])
