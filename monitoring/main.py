import psutil
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
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

    return response
