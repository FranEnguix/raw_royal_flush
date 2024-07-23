from data.algorithm import AlgorithmData
from data.log import LogData
from agent.launcher import LauncherAgent


class AppData:
    def __init__(
        self,
        algorithm: AlgorithmData,
        log: LogData = None,
        xmpp_address: str = "localhost",
        launcher_agent_web_address: str = "0.0.0.0",
        launcher_agent_web_port: int = 10000,
    ) -> None:
        self.log: LogData = None

    def get_launcher_agent(self) -> LauncherAgent:
        pass
