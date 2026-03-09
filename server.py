from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from execution.hps_engine import HPSEngine
import traceback

app = FastAPI(title="HealSim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimRequest(BaseModel):
    base_stats: dict
    upg_stats: dict
    talents: dict
    fight_style: str
    fight_length: int
    healing_requirement: str = "Balanced"
    dungeon_name: str | None = None

@app.post("/api/simulate")
def run_simulation(req: SimRequest):
    try:
        # Simulate Base
        engine_base = HPSEngine(
            stats=req.base_stats,
            talents=req.talents,
            fight_style=req.fight_style,
            fight_length_seconds=req.fight_length,
            healing_req=req.healing_requirement,
            dungeon_name=req.dungeon_name
        )
        base_result = engine_base.simulate()
        
        # Simulate Upgraded (Base + Upg)
        total_stats = {k: req.base_stats.get(k, 0) + req.upg_stats.get(k, 0) for k in req.base_stats.keys()}
        engine_upg = HPSEngine(
            stats=total_stats,
            talents=req.talents,
            fight_style=req.fight_style,
            fight_length_seconds=req.fight_length,
            healing_req=req.healing_requirement,
            dungeon_name=req.dungeon_name
        )
        upg_result = engine_upg.simulate()
        
        # We manipulate the "potentialHps" output of the basic result so it returns the Upgrade difference
        base_result["metrics"]["potentialHps"] = upg_result["metrics"]["realHpsRaw"]
        
        # Calculate Percentage Increase
        base_val = base_result["metrics"]["realHpsRaw"]
        upg_val = upg_result["metrics"]["realHpsRaw"]
        
        increase_pct = 0.0
        if base_val > 0:
            increase_pct = ((upg_val - base_val) / base_val) * 100
            
        # Format the numbers perfectly
        base_result["metrics"]["realHps"] = f"{base_val / 1000:.1f}k"
        base_result["metrics"]["potentialHps"] = f"{upg_val / 1000:.1f}k"
        
        base_result["metrics"]["increase_hps"] = upg_val - base_val
        base_result["metrics"]["increase_pct"] = increase_pct
        
        
        if increase_pct > 0:
            base_result["insights"].insert(0, {"type": "success", "message": f"Dressing this new gear yields a +{increase_pct:.2f}% Healing Output Upgrade!"})
        elif increase_pct < 0:
            base_result["insights"].insert(0, {"type": "error", "message": f"Warning: This gear swap results in a {increase_pct:.2f}% HPS LOSS!"})
        else:
            base_result["insights"].insert(0, {"type": "info", "message": "This gear swap does not noticeably impact your HPS."})
            
        return base_result
    except Exception as e:
        print(traceback.format_exc())
        return {"error": str(e)}

# Serve static files (the SPA frontend)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
