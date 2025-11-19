import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../build"))
import physics_core as pc

sim = pc.Simulator()
sim.add(pc.Entity("Sole", 5000, 5000, 2e30, 0))
sim.add(pc.Entity("Terra", 5000, 5500, 6e24, 0))
sim.add(pc.Entity("Elettrone", 5002, 5000, 9.1e-31, -1.6e-19))
sim.dt = 10.0

for _ in range(10):
    sim.step(10)
    print(sim.snapshot())
