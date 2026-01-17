from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess
import uuid
import os
import sys
import json
import logging
import configparser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("inputs", exist_ok=True)
os.makedirs("media", exist_ok=True)

app.mount("/media", StaticFiles(directory="media"), name="media")


# ---------------- Generate Endpoint ----------------
@app.post("/generate")
async def generate_visualization(data: dict):
    try:
        logger.info(f"Received request: {data}")

        uid = str(uuid.uuid4())
        cfg_path = f"inputs/{uid}.cfg"

        problem_type = data.get("type", "standard")

        # ---------- Create config file ----------
        config = configparser.ConfigParser()
        config["INPUT"] = {"type": problem_type}

        if problem_type == "standard":
            scene_name = "LinearProgrammingFull"
            config["INPUT"]["objective"] = data["objective"]
            config["INPUT"]["constraints"] = ";".join(data["constraints"])

        elif problem_type == "transportation":
            scene_name = "TransportationProblem"
            config["INPUT"]["supply"] = ",".join(map(str, data["supply"]))
            config["INPUT"]["demand"] = ",".join(map(str, data["demand"]))
            config["INPUT"]["costs"] = ";".join(
                ",".join(map(str, row)) for row in data["costs"]
            )

        elif problem_type == "tsp":
            scene_name = "TravellingSalesmanProblem"
            config["INPUT"]["cities"] = ",".join(data["cities"])
            config["INPUT"]["distances"] = ";".join(
                ",".join(map(str, row)) for row in data["distances"]
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid problem type")

        with open(cfg_path, "w") as f:
            config.write(f)

        logger.info(f"Config written to {cfg_path}")

        if not os.path.exists("node.py"):
            raise HTTPException(status_code=500, detail="node.py not found")

        # ---------- Run Manim ----------
        cmd = [
            "manim",
            "-pql",
            "node.py",
            scene_name,
            "--config_file",
            cfg_path,
        ]

        logger.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        logger.info(result.stdout)

        if result.returncode != 0:
            logger.error(result.stderr)
            raise HTTPException(status_code=500, detail=result.stderr)

        # ---------- Locate output ----------
        video_path = f"media/videos/node/480p15/{scene_name}.mp4"
        if not os.path.exists(video_path):
            raise HTTPException(status_code=500, detail="Video not found")

        return {
            "video": f"/{video_path}",
            "scene": scene_name,
            "uid": uid,
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Manim render timed out")
    except Exception as e:
        logger.error(str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "LP Visualizer API running"}
