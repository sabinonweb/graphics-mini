# 📊 Operations Research Visualizer

An interactive web application that generates beautiful, animated visualizations for Operations Research problems using [Manim](https://www.manim.community/) and FastAPI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Manim](https://img.shields.io/badge/manim-community-orange.svg)

## ✨ Features

* **Linear Programming (LP)** - Visualize feasible regions, constraint lines, and optimal solutions
* **Transportation Problem** - Animated network flows with cost optimization using Vogel's Approximation Method
* **Travelling Salesman Problem (TSP)** - Graph visualization with optimal/greedy tour solutions

### 🎥 What You Get

* **High-quality animations** (1080p @ 60fps)
* **Dynamic problem solving** - Input your own constraints, costs, and parameters
* **Mathematical optimization** - Real algorithms solving real problems
* **Beautiful visualizations** - Professional-grade mathematical animations

## 🏗️ Architecture

```
┌─────────────┐      HTTP POST      ┌──────────────┐
│   Frontend  │ ─────────────────► │   FastAPI    │
│  (Browser)  │                     │   Backend    │
└─────────────┘                     └──────┬───────┘
                                           │
                                           │ Generates
                                           │ Config File
                                           ▼
                                    ┌──────────────┐
                                    │    Manim     │
                                    │   Renderer   │
                                    └──────┬───────┘
                                           │
                                           │ Creates
                                           │ MP4 Video
                                           ▼
                                    ┌──────────────┐
                                    │    Static    │
                                    │    Files     │
                                    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

* Python 3.8 or higher
* FFmpeg (required by Manim)
* LaTeX distribution (MikTeX, TeX Live, or MacTeX)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/or-visualizer.git
   cd or-visualizer
   ```
2. **Create virtual environment**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install manim
   pip install fastapi uvicorn
   pip install scipy numpy
   ```
4. **Install FFmpeg** (if not already installed)
   * **macOS** : `brew install ffmpeg`
   * **Ubuntu/Debian** : `sudo apt-get install ffmpeg`
   * **Windows** : Download from [ffmpeg.org](https://ffmpeg.org/download.html)
5. **Install LaTeX** (if not already installed)
   * **macOS** : `brew install --cask mactex`
   * **Ubuntu/Debian** : `sudo apt-get install texlive-full`
   * **Windows** : Download [MikTeX](https://miktex.org/download)

### Running the Application

1. **Start the FastAPI server**

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`
2. **Test the API**

   ```bash
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{
       "type": "standard",
       "objective": "3x1 + 2x2",
       "constraints": ["2x1 + x2 <= 8", "x1 + 2x2 <= 10"]
     }'
   ```
3. **Access the video**
   The response will contain a path to the generated MP4 file:

   ```json
   {
     "video": "/media/videos/node/1080p60/LinearProgrammingFull.mp4",
     "scene": "LinearProgrammingFull",
     "uid": "f89b76d4-551e-4157-88c9-7dec87b873ad"
   }
   ```

## 📖 API Documentation

### Endpoints

#### `POST /generate`

Generate a visualization for an OR problem.

**Request Body:**

##### Linear Programming

```json
{
  "type": "standard",
  "objective": "5x1 + 3x2",
  "constraints": [
    "x1 + 2x2 <= 12",
    "3x1 + x2 <= 15",
    "x1 >= 0",
    "x2 >= 0"
  ]
}
```

##### Transportation Problem

```json
{
  "type": "transportation",
  "supply": [20, 30, 25],
  "demand": [15, 25, 35],
  "costs": [
    [8, 6, 10],
    [9, 12, 13],
    [14, 9, 16]
  ]
}
```

##### Travelling Salesman Problem

```json
{
  "type": "tsp",
  "cities": ["A", "B", "C", "D"],
  "distances": [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
  ]
}
```

**Response:**

```json
{
  "video": "/media/videos/node/1080p60/LinearProgrammingFull.mp4",
  "scene": "LinearProgrammingFull",
  "uid": "unique-id-here"
}
```

## 🧮 How It Works

### 1. Linear Programming Solver

The LP visualizer:

* **Parses** objective functions and constraints using regex
* **Finds corner points** by calculating intersections of constraint lines
* **Filters** feasible points based on all constraints
* **Evaluates** the objective function at each corner point
* **Animates** the objective function sliding to the optimal value

 **Algorithm** : Graphical method for 2-variable LP problems

### 2. Transportation Problem Solver

The transportation visualizer:

* **Implements** Vogel's Approximation Method (VAM)
* **Calculates** penalty costs for rows and columns
* **Allocates** shipments to minimize total transportation cost
* **Animates** the optimal allocation network

 **Algorithm** : Vogel's Approximation Method (near-optimal heuristic)

### 3. TSP Solver

The TSP visualizer:

* **Small instances (≤10 cities)** : Brute force enumeration for optimal solution
* **Large instances (>10 cities)** : Nearest neighbor heuristic
* **Animates** the tour with arrows showing the path

 **Algorithms** :

* Exact: Complete enumeration
* Heuristic: Nearest neighbor greedy algorithm

## ⚙️ Configuration

### Manim Quality Settings

The application uses high-quality rendering by default (`-pqh`):

* **Resolution** : 1920×1080
* **Frame rate** : 60 fps
* **Format** : MP4

To change quality, edit `main.py`:

```python
cmd = [
    "manim",
    "-pqm",  # Change to -pql (low), -pqm (medium), or -pqh (high)
    "node.py",
    scene_name,
    "--config_file",
    cfg_path,
]
```

### Timeout Settings

Default render timeout is 120 seconds. To change:

```python
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=180,  # Change timeout here
)
```

## 🐛 Troubleshooting

### "Video not found" error

* Check that Manim installed correctly: `manim --version`
* Ensure FFmpeg is installed: `ffmpeg -version`
* Verify LaTeX installation: `latex --version`

### "Config file not found" error

* Ensure the `inputs/` directory exists
* Check file permissions

### Rendering timeout

* Increase timeout in `main.py`
* Use lower quality setting (`-pql` or `-pqm`)
* Simplify the problem (fewer constraints/cities)

### LaTeX errors

* Install full LaTeX distribution
* On Ubuntu: `sudo apt-get install texlive-full`
* On macOS: `brew install --cask mactex`📝 License
