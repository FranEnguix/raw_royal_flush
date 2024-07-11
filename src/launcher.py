import asyncio
import spade

from aioxmpp import JID
from aiohttp import web
from agent.acol import ACoLAgent
from agent.launcher import LauncherAgent
from agent.atest import Agent1


async def main():
    domain = "localhost"
    # domain = "gtirouter.dsic.upv.es"

    number_of_agents = 5

    agents = []
    starter_neighbours = {
        JID.fromstr(f"fen_ag{num}@{domain}") for num in list(range(number_of_agents))
    }
    for ag_id in range(number_of_agents):
        agent_name = f"fen_ag{ag_id}"
        jid = f"{agent_name}@{domain}"
        neighbours = starter_neighbours - set([JID.fromstr(jid)])
        agent = ACoLAgent(
            jid=jid,
            password="ag",
            starter_neighbours=neighbours,
            observers=[JID.fromstr(f"fen_launcher@{domain}")],
        )
        agents.append(agent)

    launcher = LauncherAgent(jid=f"fen_launcher@{domain}", password="ag", agents=agents)

    await launcher.start(auto_register=True)
    launcher.web.start(hostname="0.0.0.0", port="10000")

    print("Waiting..")
    await spade.wait_until_finished(agents=launcher.agents)
    await spade.wait_until_finished(agents=launcher)


if __name__ == "__main__":
    print(f"Starting spade {spade.__version__}...")
    spade.run(main())
