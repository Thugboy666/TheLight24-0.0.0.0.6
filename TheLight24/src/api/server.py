import os, subprocess
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ai.ethics_guard import EthicsGuardian
from ai.blockchain_mock import Ledger
from ai.governance import Governance
from ai.memory_layer import MemoryLayer

from .sim_api import router as sim_router
from .ecom_api import router as ecom_router

app = FastAPI(title="TheLight24 v6.4 API")

ethics=EthicsGuardian(); ledger=Ledger()
gov=Governance(); mem=MemoryLayer()

@app.get("/health")
def health():
    return {"ok":True,"ver":"v6.4","rules":len(ethics.rules),"memory":len(mem.mem)}

@app.get("/ledger/verify")
def ledger_verify(): return {"ok":ledger.verify()}

@app.post("/ethics/reload")
def ethics_reload(): ethics._load_rules(); return {"ok":True,"rules":len(ethics.rules)}

@app.post("/backup")
def backup_now():
    p=subprocess.run(["bash","scripts/backup_system.sh"],capture_output=True,text=True)
    return {"ok":p.returncode==0,"stdout":p.stdout}

@app.get("/memory")
def memory(keyword: str = None):
    if keyword: return {"results":mem.recall(keyword)}
    return {"summary":mem.summarize()}

@app.post("/vote")
def vote(user:str,proposal:str,choice:str):
    vid=gov.vote(user,proposal,choice)
    return {"vote_id":vid,"summary":gov.summary()}

@app.post("/rep")
def reputation(user:str,delta:float):
    val=gov.reputation(user,delta)
    return {"reputation":val}

# Routers
app.include_router(sim_router)
app.include_router(ecom_router)

# Static Merchant Panel
if os.path.isdir("web/merchant"):
    app.mount("/merchant", StaticFiles(directory="web/merchant", html=True), name="merchant")
