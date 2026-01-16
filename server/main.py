from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Union
import json
import subprocess
import uuid
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("inputs", exist_ok=True)
os.makedirs("media", exist_ok=True)

try:
    if os.path.exists("media"):
        app.mount("/media", StaticFiles(directory="media"), name="media")
except Exception as e:
    logger.warning(f"Could not mount media directory: {e}")


class StandardLPInput(BaseModel):
    type: str = "standard"
    objective: str
    constraints: List[str]


class TransportationInput(BaseModel):
    type: str = "transportation"
    supply: List[float]
    demand: List[float]
    costs: List[List[float]]


class TSPInput(BaseModel):
    type: str = "tsp"
    cities: List[str]
    distances: List[List[float]]


@app.post("/generate")
async def generate_visualization(data: dict):
    try:
        logger.info(f"Received request: {data}")
        
        # Create unique ID for this request
        uid = str(uuid.uuid4())
        input_file = f"inputs/{uid}.json"
        
        # Save input data
        with open(input_file, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved input to {input_file}")
        
        problem_type = data.get("type", "standard")
        
        if problem_type == "standard":
            scene_name = "LinearProgrammingFull"
        elif problem_type == "transportation":
            scene_name = "TransportationProblem"
        elif problem_type == "tsp":
            scene_name = "TravellingSalesmanProblem"
        else:
            raise HTTPException(status_code=400, detail=f"Invalid problem type: {problem_type}")
        
        logger.info(f"Using scene: {scene_name}")
        
        if not os.path.exists("node.py"):
            raise HTTPException(
                status_code=500,
                detail="node.py not found. Please create the Manim scenes file."
            )
        
        cmd = [
            "manim",
            "-pql",
            "node.py",
            scene_name,
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        logger.info(f"Manim stdout: {result.stdout}")
        
        if result.returncode != 0:
            logger.error(f"Manim stderr: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Manim error (return code {result.returncode}): {result.stderr}"
            )
        
        # Find the generated video
        video_path = f"/media/videos/manim_scene/480p15/{scene_name}.mp4"
        full_path = f"media/videos/manim_scene/480p15/{scene_name}.mp4"
        
        if not os.path.exists(full_path):
            alt_path = f"media/videos/node/480p30/{scene_name}.mp4"
            if os.path.exists(alt_path):
                video_path = f"/media/videos/node/480p30/{scene_name}.mp4"
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Video file not found at expected location: {full_path}"
                )
        
        logger.info(f"Video generated successfully at {video_path}")
        
        return {
            "video": video_path,
            "uid": uid,
            "scene": scene_name
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Manim rendering timed out")
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/")
def root():
    return {"message": "LP Visualizer API is running"}


@app.get("/test")
def test():
    """Test endpoint to verify setup"""
    return {
        "manim_scene_exists": os.path.exists("manim_scene.py"),
        "inputs_dir_exists": os.path.exists("inputs"),
        "media_dir_exists": os.path.exists("media"),
        "current_dir": os.getcwd(),
        "python_version": sys.version
    }


if __name__ == "__main__":
    import uvicorn
    # Use localhost instead of 0.0.0.0 for better compatibility
    uvicorn.run(app, host="127.0.0.1", port=8000)