import os
import re
import psutil
import uvicorn
from fastapi import FastAPI
from mcipc.rcon.je import Client


app = FastAPI()


@app.get("/status")
async def status():
    response = {}

    # CPU
    response["cpu_usage"] = psutil.cpu_percent(interval=1)

    # RAM
    memory = psutil.virtual_memory()
    response["ram_usage"] = round(memory.percent, 1)
    response["ram_total"] = memory.total
    response["ram_available"] = memory.available
    response["ram_used"] = memory.used

    # LOADS
    response["load_1"], response["load_5"], response["load_15"] = psutil.getloadavg()

    # DISK - VOLUME
    try:
        volume = psutil.disk_usage("/mnt/volume-tassadar/")

        response["volume_usage"] = volume.percent
        response["volume_total"] = volume.total
        response["volume_used"] = volume.used
    except:
        pass

    # DISK - ROOT
    try:
        volume = psutil.disk_usage("/")

        response["storage_usage"] = volume.percent
        response["storage_total"] = volume.total
        response["storage_used"] = volume.used
    except:
        pass

    try:
        with Client("127.0.0.1", 25575, passwd=os.getenv("SERVER_RCON")) as client:
            response["server_players"] = client.list().online

            spark = re.findall("\d+\.\d+", client.run("spark tps"))

            response["server_tps_5s"] = spark[0]
            response["server_tps_10s"] = spark[1]
            response["server_tps_15m"] = spark[4]

            response["server_tick_min"] = spark[5]
            response["server_tick_med"] = spark[6]
            response["server_tick_max"] = spark[7]

            response["server_online"] = 1
    except:
        response["server_online"] = 0

    return response
