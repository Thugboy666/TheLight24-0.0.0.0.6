from ai.neural_core import NeuralCore

def test_forward_shapes():
    nc = NeuralCore(layers=[64,128,64])
    out = nc.forward([0.1,0.2,0.3])
    assert isinstance(out, list)
    assert len(out) == 64

def test_reason_score_range():
    nc = NeuralCore(layers=[32,64,32])
    score = nc.reason([0.2,0.3], [1,2,3,4,5])
    assert -10.0 < score < 10.0  # range largo ma finito
