import asyncio
import time

from aioxmpp import JID
import networkx as nx

from concurrent.futures import CancelledError
from threading import Thread
from spade.agent import Agent
from base import AgentBase, AgentNodeBase


class LauncherAgent(AgentBase):
    def __init__(
        self,
        jid: str,
        password: str,
        neighbours: list[JID],
        agents: list[AgentNodeBase],
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
        self.agents: list[AgentNodeBase] = agents
        self.threads: list[Thread] = []
        self.launched_agents: dict[AgentNodeBase, bool] = {
            a: False for a in self.agents
        }

    def launch_agents(self) -> None:
        for agent in self.agents:
            try:
                t = Thread(target=self.launch_agent, args=[agent])
                t.daemon = True
                t.name = str(agent.jid)
                self.threads.append(t)
                t.start()
                self.launched_agents[agent] = True
                print(f"[{agent.jid}] launched.")
            except RuntimeError as e:
                print(f"[{agent.jid}] exploded before being launched, because: {e}.")

    def any_agent_alive(self) -> bool:
        return any(agent.is_alive() for agent in self.agents)

    def all_agents_are_launched(self) -> bool:
        return all(self.launched_agents.values())

    def wait_for_agents(self) -> None:
        while self.any_agent_alive():
            time.sleep(1)

    def wait_for_agent_threads(self) -> None:
        for thread in self.threads:
            thread.join()

    def stop_agents(self) -> None:
        for agent in self.agents:
            if agent.is_alive():
                future = agent.stop()
                future.result()

    async def aync_wait_for_agents(self) -> None:
        while self.any_agent_alive():
            await asyncio.sleep(1)

    async def async_stop_agents(self) -> None:
        for agent in self.agents:
            await agent.stop()

    async def web_start_agents(self, request):
        post_parameters = await request.post()

    def launch_agent(self, agent: AgentNodeBase) -> None:
        try:
            future = agent.start(auto_register=True)
            future.result()
        except CancelledError as e:
            print(f"[{agent.jid}] cancelled.")
        finally:
            print(f"[{agent.jid}] ending thread.")
