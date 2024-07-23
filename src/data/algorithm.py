from dataclasses import dataclass


@dataclass
class AlgorithmData:
    name: str
    description: str


FLAMAS = AlgorithmData(name="FLaMAS", description="Centralized FL with agents.")
COL = AlgorithmData(
    name="CoL", description="Decentralized and synchronous FL with agents."
)
ACOL = AlgorithmData(
    name="ACoL", description="Decentralized and asynchronous FL with agents."
)
ACOAL = AlgorithmData(
    name="ACoaL",
    description="Decentralized and asynchronous FL with agents and coalitions.",
)
