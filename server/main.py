import configparser
import fastapi
import os
import subprocess
import uuid
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs("input", exist_ok=True)
os.makedirs("media", exist_ok=True)

app.mount("/media", StaticFiles(directory="media"), name="media")

@app.post("/generate")
async def generate(data: dict):
    try: 
        logger.info(f"Received request: {data}")
        
        uid = str(uuid.uuid4())
        cfg_path = f"input/{uid}.cfg"
        
        problem_type = data.get("type", "standard")
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
            config["INPUT"]["costs"] = ";".join(",".join(map(str, row)) for row in data["costs"])
            
        elif problem_type == "tsp":
            scene_name = "TravellingSalesmanProblem"
            config["INPUT"]["cities"] = ",".join(map(str, data["cities"]))
            config["INPUT"]["distances"] = ";".join(
                ",".join(map(str, row)) for row in data["distances"]
            )

        else:
            raise fastapi.HTTPException(status_code=400, detail="Invalid problem type")
        
        with open(cfg_path, "w") as f:
            config.write(f)
            
        logger.info(f"Config written to {cfg_path}")
        
        if not os.path.exists("node.py"):
            raise fastapi.HTTPException(status_code=500, detail="node.py not found")
            
        cmd = [
            "manim",
            "-pql",
            "node.py",
            scene_name,
            "--config_file",
            cfg_path
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        logger.info(result.stdout)
        
        if result.returncode != 0:
            logger.error(result.stderr)
            raise fastapi.HTTPException(status_code=500, detail=result.stderr)
        
        video_path = f"media/videos/node/480p15/{scene_name}.mp4"
        if not os.path.exists(video_path):
            raise fastapi.HTTPException(status_code=500, detail="Video not found")
        
        return {
            "video": f"/{video_path}",
            "scene": scene_name,
            "uid": uid
        }
        
    except subprocess.TimeoutExpired:
        raise fastapi.HTTPException(status_code=500, detail="Manim render timed out")
    except Exception as e:
        logger.error(str(e), exc_info=True)
        raise fastapi.HTTPException(status_code=500, detail=str(e))
        

