# TheLight24 v6 – Universe orchestrator
import json, os
import numpy as np
from .physics_core import PhysicsCore, PhysicsConfig

class Universe:
    """
    Carica scenari, gestisce stato, integra e fornisce snapshot per la GUI.
    """
    def __init__(self):
        self.core = None
        self.cfg  = PhysicsConfig()
        self.t    = 0.0
        self.dt_last = 0.01

    def load_from_json(self, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        pos = np.array(data["pos"], dtype=np.float64)   # [[x,y,z],...]
        vel = np.array(data["vel"], dtype=np.float64)
        mass = np.array(data["mass"], dtype=np.float64)
        charge = np.array(data.get("charge",[0.0]*len(mass)), dtype=np.float64)

        pc = data.get("physics", {})
        self.cfg = PhysicsConfig(
            grav=pc.get("grav", True),
            coulomb=pc.get("coulomb", False),
            yukawa=pc.get("yukawa", False),
            yukawa_lambda=pc.get("yukawa_lambda", 1e9),
            yukawa_alpha=pc.get("yukawa_alpha", 0.1),
            drag=pc.get("drag", False),
            drag_gamma=pc.get("drag_gamma", 0.0),
            softening=pc.get("softening", 1e3),
        )
        self.core = PhysicsCore(pos, vel, mass, charge, self.cfg)
        self.t = 0.0
        self.dt_last = 0.01

    def step(self, dt=None):
        if self.core is None: return 0.0
        dt_used = self.core.step(dt)
        self.t += dt_used
        self.dt_last = dt_used
        return dt_used

    def snapshot(self, max_particles=None):
        if self.core is None: return {}
        N = self.core.N if max_particles is None else min(self.core.N, max_particles)
        return {
            "t": self.t,
            "dt": self.dt_last,
            "N": N,
            "pos": self.core.pos[:N].tolist(),
            "vel": self.core.vel[:N].tolist(),
            "mass": self.core.mass[:N].tolist(),
        }
