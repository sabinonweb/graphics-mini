import { useState } from "react";

function App() {
  const [problemType, setProblemType] = useState("standard");
  const [objective, setObjective] = useState("");
  const [constraints, setConstraints] = useState("");
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [supply, setSupply] = useState("");
  const [demand, setDemand] = useState("");
  const [costs, setCosts] = useState("");

  const [cities, setCities] = useState("");
  const [distances, setDistances] = useState("");

  const loadExample = () => {
    if (problemType === "standard") {
      setObjective("3x1 + 2x2");
      setConstraints("2x1 + x2 <= 8\nx1 + 2x2 <= 10\nx1 >= 0\nx2 >= 0");
    } else if (problemType === "transportation") {
      setSupply("20, 30, 25");
      setDemand("15, 25, 35");
      setCosts("8,6,10; 9,12,13; 14,9,16");
    } else if (problemType === "tsp") {
      setCities("A, B, C, D");
      setDistances("0,10,15,20; 10,0,35,25; 15,35,0,30; 20,25,30,0");
    }
  };

  const submit = async () => {
    setLoading(true);
    setError(null);
    setVideo(null);

    try {
      let body;
      if (problemType === "standard") {
        body = {
          type: "standard",
          objective,
          constraints: constraints.split("\n").filter((c) => c.trim()),
        };
      } else if (problemType === "transportation") {
        body = {
          type: "transportation",
          supply: supply.split(",").map((s) => parseFloat(s.trim())),
          demand: demand.split(",").map((d) => parseFloat(d.trim())),
          costs: costs
            .split(";")
            .map((row) => row.split(",").map((c) => parseFloat(c.trim()))),
        };
      } else if (problemType === "tsp") {
        body = {
          type: "tsp",
          cities: cities.split(",").map((c) => c.trim()),
          distances: distances
            .split(";")
            .map((row) => row.split(",").map((d) => parseFloat(d.trim()))),
        };
      }

      const res = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setVideo("http://localhost:8000" + data.video);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: "40px",
        maxWidth: "900px",
        margin: "0 auto",
        fontFamily: "system-ui, -apple-system, sans-serif",
        backgroundColor: "white",
      }}
    >
      <h1
        style={{
          fontSize: "32px",
          marginBottom: "10px",
          color: "#1a1a1a",
        }}
      >
        Linear Programming Visualizer
      </h1>
      <p
        style={{
          color: "#666",
          marginBottom: "30px",
          fontSize: "14px",
        }}
      >
        Visualize LP, Transportation, and TSP problems with Manim
      </p>

      {/* Problem Type Selection */}
      <div style={{ marginBottom: "25px" }}>
        <label
          style={{
            display: "block",
            fontWeight: "600",
            marginBottom: "8px",
            color: "#333",
          }}
        >
          Problem Type
        </label>
        <div style={{ display: "flex", gap: "10px" }}>
          {["standard", "transportation", "tsp"].map((type) => (
            <button
              key={type}
              onClick={() => setProblemType(type)}
              style={{
                padding: "10px 20px",
                border:
                  problemType === type
                    ? "2px solid #3b82f6"
                    : "2px solid #e5e7eb",
                borderRadius: "6px",
                background: problemType === type ? "#eff6ff" : "white",
                cursor: "pointer",
                fontWeight: problemType === type ? "600" : "400",
                color: problemType === type ? "#3b82f6" : "#666",
                transition: "all 0.2s",
              }}
            >
              {type === "standard"
                ? "Standard LP"
                : type === "transportation"
                ? "Transportation"
                : "TSP"}
            </button>
          ))}
        </div>
      </div>

      {/* Standard LP Inputs */}
      {problemType === "standard" && (
        <>
          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Objective Function
            </label>
            <input
              placeholder="e.g., 3x1 + 2x2"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Constraints (one per line)
            </label>
            <textarea
              rows="6"
              placeholder="e.g.,&#10;2x1 + x2 <= 8&#10;x1 + 2x2 <= 10&#10;x1 >= 0&#10;x2 >= 0"
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                fontFamily: "monospace",
                boxSizing: "border-box",
              }}
            />
          </div>
        </>
      )}

      {/* Transportation Problem Inputs */}
      {problemType === "transportation" && (
        <>
          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Supply (comma-separated)
            </label>
            <input
              placeholder="e.g., 20, 30, 25"
              value={supply}
              onChange={(e) => setSupply(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Demand (comma-separated)
            </label>
            <input
              placeholder="e.g., 15, 25, 35"
              value={demand}
              onChange={(e) => setDemand(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Cost Matrix (rows separated by semicolons)
            </label>
            <textarea
              rows="4"
              placeholder="e.g.,&#10;8,6,10; 9,12,13; 14,9,16"
              value={costs}
              onChange={(e) => setCosts(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                fontFamily: "monospace",
                boxSizing: "border-box",
              }}
            />
          </div>
        </>
      )}

      {/* TSP Inputs */}
      {problemType === "tsp" && (
        <>
          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Cities (comma-separated)
            </label>
            <input
              placeholder="e.g., A, B, C, D"
              value={cities}
              onChange={(e) => setCities(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label
              style={{
                display: "block",
                fontWeight: "600",
                marginBottom: "8px",
                color: "#333",
              }}
            >
              Distance Matrix (rows separated by semicolons)
            </label>
            <textarea
              rows="4"
              placeholder="e.g.,&#10;0,10,15,20; 10,0,35,25; 15,35,0,30; 20,25,30,0"
              value={distances}
              onChange={(e) => setDistances(e.target.value)}
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #e5e7eb",
                borderRadius: "6px",
                fontSize: "14px",
                fontFamily: "monospace",
                boxSizing: "border-box",
              }}
            />
          </div>
        </>
      )}

      {/* Action Buttons */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "30px",
        }}
      >
        <button
          onClick={submit}
          disabled={loading}
          style={{
            padding: "12px 24px",
            background: loading ? "#9ca3af" : "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontWeight: "600",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "14px",
            transition: "background 0.2s",
          }}
        >
          {loading ? "Generating..." : "Generate Visualization"}
        </button>

        <button
          onClick={loadExample}
          style={{
            padding: "12px 24px",
            background: "white",
            color: "#3b82f6",
            border: "2px solid #3b82f6",
            borderRadius: "6px",
            fontWeight: "600",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          Load Example
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div
          style={{
            padding: "16px",
            background: "#fee2e2",
            border: "2px solid #ef4444",
            borderRadius: "6px",
            color: "#991b1b",
            marginBottom: "20px",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Video Display */}
      {video && (
        <div
          style={{
            marginTop: "30px",
            border: "2px solid #e5e7eb",
            borderRadius: "8px",
            overflow: "hidden",
            boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
          }}
        >
          <video
            src={video}
            controls
            style={{
              width: "100%",
              display: "block",
            }}
          />
        </div>
      )}

      {/* Instructions */}
      <div
        style={{
          marginTop: "40px",
          padding: "20px",
          background: "#f9fafb",
          borderRadius: "8px",
          fontSize: "13px",
          color: "#4b5563",
        }}
      >
        <h3 style={{ marginTop: 0, fontSize: "16px", color: "#1a1a1a" }}>
          How to Use
        </h3>
        <ul style={{ marginBottom: 0, paddingLeft: "20px" }}>
          <li>
            <strong>Standard LP:</strong> Enter objective function and
            constraints
          </li>
          <li>
            <strong>Transportation:</strong> Provide supply, demand, and cost
            matrix
          </li>
          <li>
            <strong>TSP:</strong> Enter city names and distance matrix
          </li>
        </ul>
      </div>
    </div>
  );
}

export default App;
