import time

from agent.launcher import LauncherAgent
from data.app import AppData
from data.algorithm import AlgorithmData, FLAMAS, COL, ACOL, ACOAL
from log.log import CsvLogHandler

if __name__ == "__main__":
    log = CsvLogHandler()
    app = AppData(algorithm=ACOL, log=log)
    launcher = app.get_launcher_agent()
    future = launcher.start(auto_register=True)
    future.result()
    try:
        while not launcher.all_agents_are_launched():
            time.sleep(1)
        print(
            f"[{launcher.name}] All agents are launched. Waiting for them to finish..."
        )
        launcher.wait_for_agents()
    except KeyboardInterrupt:
        print("Experiment cancelled by keyboard interruption.")
    finally:
        launcher.stop_agents()
        future = launcher.stop()
        future.result()
        launcher.wait_for_agent_threads()
