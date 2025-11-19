import math, random
from typing import List, Dict

class Neuron:
    def __init__(self, nid:int, kind:str="hidden"):
        self.id = nid
        self.kind = kind
        self.bias = random.uniform(-0.1,0.1)
        self.value = 0.0
        self.out = {}  # target_id -> weight

class NeuralCore:
    def __init__(self, layers=[256,512,512,256]):
        self.neurons: Dict[int, Neuron] = {}
        self.layers = []
        nid = 0
        for size in layers:
            layer = []
            for _ in range(size):
                n = Neuron(nid, "hidden")
                self.neurons[nid] = n
                layer.append(nid)
                nid += 1
            self.layers.append(layer)
        for l in range(len(self.layers)-1):
            for i in self.layers[l]:
                for j in self.layers[l+1]:
                    self.neurons[i].out[j] = random.uniform(-0.05,0.05)
        self.context = [0.0]*64
        self.temp = 0.9

    def _incoming(self, j):
        inc = {}
        for i, n in self.neurons.items():
            if j in n.out: inc[i] = n.out[j]
        return inc

    def forward(self, inputs: List[float]) -> List[float]:
        first = self.layers[0]
        for k, val in enumerate(inputs[:len(first)]):
            self.neurons[first[k]].value = val
        for k in range(len(inputs), len(first)):
            c = self.context[k % len(self.context)]
            self.neurons[first[k]].value = c
        for l in range(1, len(self.layers)):
            for j in self.layers[l]:
                s = self.neurons[j].bias
                for i, w in self._incoming(j).items():
                    s += self.neurons[i].value * w
                # GELU-like
                self.neurons[j].value = 0.5*s*(1+math.tanh(0.797884*(s+0.044715*s*s*s)))
        last_vals = [self.neurons[j].value for j in self.layers[-1]]
        avg = sum(last_vals)/max(1,len(last_vals))
        self.context = [(1-self.temp)*c + self.temp*avg for c in self.context]
        return last_vals

    def reason(self, signal: List[float], tokens: List[int]) -> float:
        out = self.forward(signal + [t/4096.0 for t in tokens[:32]])
        return sum(out)/len(out)
