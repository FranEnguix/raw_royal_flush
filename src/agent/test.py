from aioxmpp import JID
from base import AgentNodeBase
from data.algorithm import AlgorithmData


class TestAgent(AgentNodeBase):
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
            jid,
            password,
            observers,
            neighbours,
            algorithm,
            web_address,
            web_port,
            verify_security,
        )
