import asyncio
import logging
import os
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from math import inf
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.parser import AssemblyParser, ParseError
from core.cache import Cache
from pipeline.controller import Pipeline

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("api")

MAX_CYCLES = 100_000
SESSION_TTL = 1800  # 30 min

sessions: dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=4)


#every 5 minutes it looks up sessions that have passed their TTL and must be killed by the janitor
#i want to prevent a memory leak, without it the sessions dictionary would increase wout end 
async def _session_janitor():
    while True:
        await asyncio.sleep(300)
        now = time.time()
        expired = [sid for sid, s in list(sessions.items()) if now - s["last_accessed"] > SESSION_TTL]
        for sid in expired:
            sessions.pop(sid, None)
        if expired:
            log.info("evicted %d stale sessions", len(expired))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_session_janitor())
    yield
    task.cancel()


app = FastAPI(title="RISC-V Performance Analyzer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000
    log.info("%s %s %d %.1fms", request.method, request.url.path, response.status_code, ms)
    return response


class SimConfig(BaseModel):
    code: str
    use_cache: bool = True
    cache_size: int = 256
    associativity: int = 2
    write_policy: str = "write-back"
    use_branch_predictor: bool = True
    ram_latency: int = 50


class SimulateRequest(SimConfig):
    max_cycles: Optional[int] = None


def _parse_code(code: str):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".s", delete=False, encoding="utf-8") as f:
        f.write(code)
        path = f.name
    try:
        parser = AssemblyParser(path)
        return parser.parse()
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.unlink(path)


def _build_pipeline(req: SimConfig) -> Pipeline:
    instructions, initial_memory = _parse_code(req.code)
    cache = None
    if req.use_cache:
        cache = Cache(
            size=req.cache_size,
            line_size=16,
            associativity=req.associativity,
            write_policy=req.write_policy,
            ram_latency=req.ram_latency,
        )
    pipeline = Pipeline(
        instructions,
        cache=cache,
        use_branch_predictor=req.use_branch_predictor,
        ram_latency=req.ram_latency,
    )
    for addr, val in initial_memory.items():
        pipeline.memory.data[addr >> 2] = val
    return pipeline


def _state(pipeline: Pipeline) -> dict:
    stages = {
        name: {
            "instruction": str(stage.instruction) if stage.instruction else None,
            "data": {k: str(v) for k, v in stage.data.items()},
        }
        for name, stage in pipeline.stages.items()
    }
    registers = {i: pipeline.registers.read(i) for i in range(32)}
    memory = {f"{i * 4:#x}": v for i, v in enumerate(pipeline.memory.data) if v != 0}
    return {
        "cycle": pipeline.cycle,
        "done": pipeline.is_done(),
        "stages": stages,
        "registers": registers,
        "memory": memory,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/simulate")
def simulate(req: SimulateRequest):
    pipeline = _build_pipeline(req)
    pipeline.run(max_cycles=min(req.max_cycles or MAX_CYCLES, MAX_CYCLES))
    return {"stats": pipeline.get_performance_stats(), "state": _state(pipeline)}


@app.post("/session")
def create_session(req: SimConfig):
    pipeline = _build_pipeline(req)
    sid = str(uuid.uuid4())
    sessions[sid] = {"pipeline": pipeline, "last_accessed": time.time()}
    return {"session_id": sid, "state": _state(pipeline)}


@app.post("/session/{sid}/step")
def step(sid: str):
    entry = sessions.get(sid)
    if not entry:
        raise HTTPException(status_code=404, detail="session negasita")
    entry["last_accessed"] = time.time()
    pipeline = entry["pipeline"]
    if pipeline.cycle == 0 or not pipeline.is_done():
        pipeline.tick()
    return {"state": _state(pipeline), "stats": pipeline.get_performance_stats()}


@app.delete("/session/{sid}")
def delete_session(sid: str):
    if sid not in sessions:
        raise HTTPException(status_code=404, detail="session negasita")
    del sessions[sid]
    return {"deleted": sid}


COMPARE_SIZES = [128, 256, 512, 1024, 2048]
COMPARE_WAYS = [1, 2, 4]
COMPARE_POLICIES = ["write-back", "write-through"]


def _run_compare(req: SimulateRequest) -> dict:
    def run_variant(**overrides):
        r = req.model_copy(update=overrides)
        p = _build_pipeline(r)
        p.run(max_cycles=req.max_cycles if req.max_cycles is not None else inf)
        stats = p.get_performance_stats()
        if p.memory.cache:
            stats["cache"] = p.memory.cache.get_stats()
        return stats

    baseline = run_variant(use_cache=False)
    variants = []
    for size in COMPARE_SIZES:
        for ways in COMPARE_WAYS:
            for policy in COMPARE_POLICIES:
                stats = run_variant(use_cache=True, cache_size=size, associativity=ways, write_policy=policy)
                variants.append({"size": size, "associativity": ways, "write_policy": policy, "stats": stats})

    return {"baseline": baseline, "variants": variants}


@app.post("/compare")
async def compare(req: SimulateRequest):
    loop = asyncio.get_event_loop()
    t0 = time.perf_counter()
    try:
        result = await loop.run_in_executor(executor, _run_compare, req)
        log.info("compare finished in %.1fs", time.perf_counter() - t0)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
