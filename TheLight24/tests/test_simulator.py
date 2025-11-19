import os, sys, pytest
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "build"))

@pytest.mark.skipif("physics_core" not in __import__("sys").modules and
                    __import__("importlib").util.find_spec("physics_core") is None,
                    reason="Modulo physics_core non trovato. Esegui la build in /build")
def test_bindings_minimal():
    import physics_core as pc
    sim = pc.Simulator()
    sim.add(pc.Entity("A", 1000, 1000, 1e5, 0))
    sim.add(pc.Entity("B", 1005, 1000, 1e5, 0))
    sim.dt = 0.1
    sim.step(5)
    snap = sim.snapshot()
    assert "Entities=2" in snap
