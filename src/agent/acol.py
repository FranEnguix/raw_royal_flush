import asyncio
import spade
import random


from aioxmpp import JID, PresenceState, PresenceShow
from aioxmpp.stanza import Presence
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour
from spade.message import Message
from spade.template import Template


class ACoLAgent(Agent):
    def __init__(
        self,
        jid: str,
        password: str,
        verify_security: bool = False,
        observers: set[JID] = None,
        starter_neighbours: set[JID] = None,
    ):
        super().__init__(jid, password, verify_security)
        self.fsm_states = {
            "setup": "SETUP_STATE",
            "train": "TRAIN_STATE",
            "send": "SEND_STATE",
            "receive": "RECEIVE_STATE",
        }
        self.observers = observers
        self.starter_neighbours = starter_neighbours

        if not self.observers:
            self.observers: set[JID] = set([])
        elif isinstance(self.observers, list):
            self.observers: set[JID] = set(self.observers)

        if not self.starter_neighbours:
            self.starter_neighbours: set[JID] = set([])
        elif isinstance(self.starter_neighbours, list):
            self.starter_neighbours: set[JID] = set(self.starter_neighbours)

    async def setup(self):
        print(f"{self.jid} created.")

        self.add_behaviour(behaviour=self.Presence(period=1))

        self.fsm_behaviour = ACoLFSMBehaviour()
        self.fsm_behaviour.add_state(
            name=self.fsm_states["setup"], state=SetupState(), initial=True
        )
        self.fsm_behaviour.add_state(name=self.fsm_states["train"], state=TrainState())
        self.fsm_behaviour.add_state(name=self.fsm_states["send"], state=SendState())
        self.fsm_behaviour.add_state(
            name=self.fsm_states["receive"], state=ReceiveState()
        )
        self.fsm_behaviour.add_transition(
            source=self.fsm_states["setup"], dest=self.fsm_states["train"]
        )
        self.fsm_behaviour.add_transition(
            source=self.fsm_states["train"], dest=self.fsm_states["send"]
        )
        self.fsm_behaviour.add_transition(
            source=self.fsm_states["send"], dest=self.fsm_states["receive"]
        )
        self.fsm_behaviour.add_transition(
            source=self.fsm_states["receive"], dest=self.fsm_states["train"]
        )
        self.add_behaviour(behaviour=self.fsm_behaviour)

    async def stop(self) -> None:
        if self.is_alive():
            print(f"[{self.jid.bare()}] Stopping agent...")
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

    def get_non_available_neighbours(self) -> set[JID]:
        available_neighbours_jids = self.get_available_neighbours()
        all_neighbours_jids = self.starter_neighbours.union(self.observers)
        return all_neighbours_jids - available_neighbours_jids

    class Presence(PeriodicBehaviour):

        def subscribe(self, agents: set[JID]) -> None:
            for jid in agents:
                self.agent.presence.subscribe(str(jid))

        def subscribe_to_non_availables(self) -> set[JID]:
            """
            Subscribe to non-subscribed neighbours and return the

            Returns:
                set[JID]: _description_
            """
            non_availables = self.agent.get_non_available_neighbours()
            if non_availables:
                print(f"[{self.agent.name}] trying to subscribe to: {non_availables}")
                self.subscribe(non_availables)
            return non_availables

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

        def on_available(self, jid: str, stanza: Presence):
            print(f"[{self.agent.name}] Agent {jid} is available.")

        def on_subscribed(self, jid: str):
            print(f"[{self.agent.name}] Agent {jid} has accepted the subscription.")
            print(
                f"[{self.agent.name}] Contacts List: {self.agent.presence.get_contacts()}"
            )

        def on_subscribe(self, jid: str):
            print(
                f"[{self.agent.name}] Agent {jid} asked for subscription. Let's aprove it."
            )
            self.agent.presence.approve(jid)

        def on_unavailable(self, jid: str, stanza: Presence) -> None:
            print(f"[{self.agent.name}] Agent {jid} is unavailable.")

        async def on_start(self) -> None:
            self.saved_available_neighbours: set[JID] = set([])
            self.agent.presence.set_available()
            self.agent.presence.on_subscribe = self.on_subscribe
            self.agent.presence.on_subscribed = self.on_subscribed
            self.agent.presence.on_available = self.on_available
            self.agent.presence.on_unavailable = self.on_unavailable
            self.agent.presence.approve_all = True
            self.agent.presence.set_presence(
                state=PresenceState(True, PresenceShow.CHAT), status="READY_ACOL"
            )

        async def run(self):
            self.subscribe_to_non_availables()
            if self.__update_available_neighbours():
                print(
                    f"[{self.agent.name}] Contacts List: {self.agent.presence.get_contacts()}"
                )


class ACoLFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[{self.agent.name}] FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"[{self.agent.name}] FSM finished at state {self.current_state}")
        await self.agent.stop()


class SetupState(State):

    async def run(self):
        print(f"[{self.agent.name}] I'm at {self.agent.fsm_states['setup']}")
        self.set_next_state(self.agent.fsm_states["train"])


class TrainState(State):

    async def run(self):
        print(f"[{self.agent.name}] I'm at {self.agent.fsm_states['train']}")
        self.set_next_state(self.agent.fsm_states["send"])
        await asyncio.sleep(2)


class SendState(State):

    async def run(self):
        print(f"[{self.agent.name}] I'm at {self.agent.fsm_states['send']}")
        neighbours: list[JID] = list(self.agent.get_available_neighbours())
        if neighbours:
            dst = str(random.choice(neighbours))
            msg = Message(
                to=dst, sender=str(self.agent.jid), body=f"prueba de {self.agent.name}"
            )
        # await self.send(msg=msg)
        self.set_next_state(self.agent.fsm_states["receive"])
        await asyncio.sleep(2)


class ReceiveState(State):

    async def run(self):
        print(f"[{self.agent.name}] I'm at {self.agent.fsm_states['receive']}")
        msg = await self.receive(timeout=5)
        if msg:
            print(f"{self.agent.name} received message: {msg.body}")
        print(
            f"[{self.agent.name}] Contacts List: {self.agent.presence.get_contacts()}"
        )
        self.set_next_state(self.agent.fsm_states["train"])
        await asyncio.sleep(2)
