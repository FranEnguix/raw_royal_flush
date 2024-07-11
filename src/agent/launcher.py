import asyncio
import spade
import random

from aioxmpp import JID, PresenceState, PresenceShow
from aioxmpp.stanza import Presence
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from threading import Thread


class LauncherAgent(Agent):
    def __init__(
        self,
        jid: str,
        password: str,
        verify_security: bool = False,
        agents: set[Agent] = None,
    ):
        super().__init__(jid, password, verify_security)
        self.agents = agents
        self.threads: list[Thread] = []

    async def web_controller(self, request):
        return {}

    async def web_stop_agents(self, request):
        await self.stop_agents()
        return {}

    async def web_stop_all_agents(self, request):
        await self.stop_agents()
        await self.stop()
        return {}

    async def stop_agents(self) -> None:
        # available_neighbours = self.get_available_neighbours()
        # for jid in available_neighbours:
        #     print(f" -- [{self.name}] unsubscribing from {jid.bare()}")
        #     self.presence.unsubscribe(f"{jid}")
        for ag in self.agents:
            if ag.is_alive():
                await ag.stop()

    def launch_agent(self, agent: Agent) -> None:
        print(f"[{agent.name}] Starting thread...")
        future = asyncio.gather(agent.start())
        future.result()
        print(f"[{agent.name}] Future ended.")

    async def setup(self) -> None:
        self.web.add_get("/launcher", lambda request: {}, "src/interface/launcher.html")
        self.web.add_get("/stopagents", self.web_stop_agents, None)
        self.web.add_get("/stopallagents", self.web_stop_all_agents, None)
        self.presence.approve_all = True
        for agent in self.agents:
            t = Thread(target=self.launch_agent, args=(agent))
            t.daemon = True
            t.name = agent.name
            self.threads.append(t)
        # coros = [ag.start(auto_register=True) for ag in self.agents]
        # await asyncio.gather(*coros)
        # for ag in self.agents:
        #     await ag.start(auto_register=True)
        self.presence.set_presence(
            state=PresenceState(True, PresenceShow.CHAT), status="READY2CONS"
        )
        self.add_behaviour(self.Presence(period=3))

    async def stop(self) -> None:
        for t in self.threads:
            if t.is_alive():
                t.join()
        if self.is_alive():
            print("Stopping the launcher agent...")
            self.presence.set_unavailable()
            available_neighbours = self.get_available_neighbours()
            for jid in available_neighbours:
                print(f" -- [{self.name}] unsubscribing from {jid.bare()}")
                self.presence.unsubscribe(f"{jid}")
            await super().stop()

    def get_available_neighbours(self) -> set[JID]:
        return {
            jid
            for (jid, value) in self.presence.get_contacts().items()
            if "presence" in value and value["presence"].show is not None
        }

    def get_non_available_neighbours(self) -> list[JID]:
        available_neighbours_jids = self.get_available_neighbours()
        all_neighbours_jids: set[JID] = {agent.jid for agent in self.agents}
        return all_neighbours_jids - available_neighbours_jids

    class Presence(PeriodicBehaviour):
        async def on_start(self) -> None:
            self.saved_available_neighbours: set[JID] = set([])
            self.agent.presence.set_available()
            self.agent.presence.on_subscribe = self.on_subscribe
            self.agent.presence.on_subscribed = self.on_subscribed
            self.agent.presence.on_available = self.on_available
            self.agent.presence.on_unavailable = self.on_unavailable
            self.agent.presence.approve_all = True
            self.agent.presence.set_presence(
                state=PresenceState(True, PresenceShow.CHAT), status="READY2CONS"
            )

        async def run(self) -> None:
            self.subscribe_to_non_availables()
            if self.__update_available_neighbours():
                print(
                    f"[{self.agent.name}] Contacts List: {self.agent.presence.get_contacts()}"
                )

        def subscribe(self, agents: set[JID]) -> None:
            for jid in agents:
                self.agent.presence.subscribe(str(jid))

        def subscribe_to_non_availables(self) -> None:
            non_availables = self.agent.get_non_available_neighbours()
            if non_availables:
                self.subscribe(non_availables)

        def __update_available_neighbours(self) -> bool:
            """
            Updates the available agents and returns if the list has been updated.

            Returns:
                bool: True if the list has been updated, False otherwise.
            """
            available_neighbours: set[JID] = self.agent.get_available_neighbours()
            if (
                len(
                    available_neighbours.symmetric_difference(
                        self.saved_available_neighbours
                    )
                )
                > 0
            ):
                self.saved_available_neighbours = available_neighbours
                return True
            return False

        def on_available(self, jid: str, stanza: Presence) -> None:
            print(f"[{self.agent.name}] Agent {jid} is available.")

        def on_subscribed(self, jid: str) -> None:
            print(f"[{self.agent.name}] Agent {jid} has accepted the subscription.")
            print(
                f"[{self.agent.name}] Contacts List: {self.agent.presence.get_contacts()}"
            )

        def on_subscribe(self, jid: str) -> None:
            print(
                f"[{self.agent.name}] Agent {jid} asked for subscription. Let's aprove it."
            )
            self.agent.presence.approve(jid)

        def on_unavailable(self, jid: str, stanza: Presence) -> None:
            print(f"[{self.agent.name}] Agent {jid} is unavailable.")
