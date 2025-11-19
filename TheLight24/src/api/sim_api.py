# FastAPI router per Universe_SIM
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..sim.universe import Universe
import os

router = APIRouter(prefix="/sim", tags=["simulation"])
UNIVERSE = Universe()

@router.post("/load")
def load(scenario: str):
    path = os.path.join("src","sim","scenarios", scenario)
    if not os.path.exists(path):
        raise HTTPException(404, f"Scenario non trovato: {scenario}")
    UNIVERSE.load_from_json(path)
    return {"ok": True, "scenario": scenario}

@router.post("/step")
def step(dt: Optional[float] = Query(None)):
    used = UNIVERSE.step(dt)
    return {"ok": True, "dt_used": used, "t": UNIVERSE.t}

@router.get("/snapshot")
def snapshot(n: Optional[int] = Query(None)):
    return UNIVERSE.snapshot(max_particles=n)

@router.get("/status")
def status():
    return {"t": UNIVERSE.t, "loaded": UNIVERSE.core is not None}
