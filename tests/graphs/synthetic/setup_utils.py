import subprocess

from time import sleep


def start_routing_server(run_server="run_server.sh", wait=3):
    # prepare data, wait
    subprocess.check_call([run_server, "true", "false", "false"])

    # run server on background
    p = subprocess.Popen(
        [run_server, "false", "true", "false"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    sleep(wait)  # give time to server to start
    return p, "http://localhost:5000/v1/match"


def stop_container(container_name="local-routing-service"):
    subprocess.call(["docker", "stop", container_name])
