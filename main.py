#!/usr/bin/env python3
import subprocess
from subprocess import PIPE, Popen
import wandb
from collections import defaultdict
from statistics import mean

hname = subprocess.check_output("hostname -I|grep -oP '(?<=192.168.0.1)\d*'", shell=True).decode().strip()
project = f"monitor_health{hname}"
wandb.init(project=project)
print(project)

func = [mean, max]

def main():
    query = "utilization.gpu,power.draw,temperature.gpu".split(",")
    proc = Popen(
        f"nvidia-smi --loop=1 --format=csv,noheader --query-gpu=index,{','.join(query)}",
        shell=True, stdout=PIPE)
    master = defaultdict(dict)
    for line in proc.stdout:
        index, *answer = line.decode().strip().split(",")
        if index == "0" and len(master) != 0:
            data = dict()
            for q, a in master.items():
                for f in func:
                    data[f"{f.__name__}.{q}"] = f(a.values())
            for q, a in master.items():
                for i, v in a.items():
                    data[f"{i}.{q}"] = v
            wandb.log(data)
        for q, a in zip(query, answer):
            master[q][index] = float(a.split()[0])

if __name__ == "__main__":
    main()
