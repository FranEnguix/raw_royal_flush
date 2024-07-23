from aioxmpp import JID
from data.algorithm import AlgorithmData
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from utilities.multipart import MultipartHandler


class AgentBase(Agent):
    def __init__(
        self,
        jid: str,
        password: str,
        neighbours: list[JID],
        web_address: str = "0.0.0.0",
        web_port: int = 10000,
        verify_security: bool = False,
    ):
        super().__init__(jid=jid, password=password, verify_security=verify_security)
        self.neighbours = neighbours
        self.web_address = web_address
        self.web_port = web_port
        self.multipart_handler = MultipartHandler()

    async def send(self, message: Message, behaviour: CyclicBehaviour = None) -> None:
        messages: list[Message] = self.multipart_handler.generate_multipart_messages(
            content=message.body, message_base=message
        )
        if messages is None:
            messages = [message]
        for msg in messages:
            if behaviour is not None:
                await behaviour.send(msg=msg)
            else:
                futures = self.dispatch(msg=msg)
                for f in futures:
                    f.result()


class AgentNodeBase(AgentBase):
    def __init__(
        self,
        jid: str,
        password: str,
        observers: list[JID],
        neighbours: list[JID],
        algorithm: AlgorithmData = None,
        web_address: str = "0.0.0.0",
        web_port: int = 10000,
        verify_security: bool = False,
    ):
        super().__init__(
            jid=jid,
            password=password,
            neighbours=neighbours,
            web_address=web_address,
            web_port=web_port,
            verify_security=verify_security,
        )
        self.observers = observers
        self.algorithm = algorithm
