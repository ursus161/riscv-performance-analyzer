import uuid
import tempfile
import os
from math import inf
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.parser import AssemblyParser, ParseError
from core.cache import Cache
from pipeline.controller import Pipeline

# hard cap regardless of client input, rate limiting against infinite loops / DoS
MAX_CYCLES = 100_000

app = FastAPI(title="RISC-V Performance Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, Pipeline] = {}


class SimulateRequest(BaseModel):
    code: str
    use_cache: bool = False
    cache_size: int = 256
    associativity: int = 2
    write_policy: str = "write-back"
    use_branch_predictor: bool = False
    ram_latency: int = 50
    max_cycles: Optional[int] = None


class SessionRequest(BaseModel):
    code: str
    use_cache: bool = False
    cache_size: int = 256
    associativity: int = 2
    write_policy: str = "write-back"
    use_branch_predictor: bool = False
    ram_latency: int = 50


def _parse_code(code: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False, encoding='utf-8') as f:
        f.write(code)
        path = f.name
    try:
        parser = AssemblyParser(path)
        return parser.parse()
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.unlink(path)


def _build_pipeline(req) -> Pipeline:
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

    pipeline = Pipeline(instructions, cache=cache, use_branch_predictor=req.use_branch_predictor,
                        ram_latency=req.ram_latency)

    for addr, val in initial_memory.items():
        pipeline.memory.data[addr >> 2] = val

    return pipeline


def _state(pipeline: Pipeline) -> dict:
    stages = {
        name: {
            'instruction': str(stage.instruction) if stage.instruction else None,
            'data': {k: str(v) for k, v in stage.data.items()},
        }
        for name, stage in pipeline.stages.items()
    }
    registers = {i: pipeline.registers.read(i) for i in range(32)}
    memory = {f"{i * 4:#x}": v for i, v in enumerate(pipeline.memory.data) if v != 0}

    return {
        'cycle': pipeline.cycle,
        'done': pipeline.is_done(),
        'stages': stages,
        'registers': registers,
        'memory': memory,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/simulate")
def simulate(req: SimulateRequest):
    pipeline = _build_pipeline(req)
    pipeline.run(max_cycles=min(req.max_cycles or MAX_CYCLES, MAX_CYCLES))
    return {
        'stats': pipeline.get_performance_stats(),
        'state': _state(pipeline),
    }


@app.post("/session")
def create_session(req: SessionRequest):
    pipeline = _build_pipeline(req)
    sid = str(uuid.uuid4())
    sessions[sid] = pipeline
    return {'session_id': sid, 'state': _state(pipeline)}


@app.post("/session/{sid}/step")
def step(sid: str):
    pipeline = sessions.get(sid)
    if not pipeline:
        raise HTTPException(status_code=404, detail="session negasita")
    # pipeline proaspat are cycle=0 si toate stage urile None => is_done() e True inainte sa inceapa
    if pipeline.cycle == 0 or not pipeline.is_done():
        pipeline.tick()
    return {'state': _state(pipeline), 'stats': pipeline.get_performance_stats()}


COMPARE_SIZES = [128, 256, 512, 1024, 2048]
COMPARE_WAYS  = [1, 2, 4]
COMPARE_POLICIES = ['write-back', 'write-through']


@app.post("/compare")
def compare(req: SimulateRequest):
    def run_variant(**overrides):
        r = req.model_copy(update=overrides)
        p = _build_pipeline(r)
        p.run(max_cycles=req.max_cycles if req.max_cycles is not None else inf)
        stats = p.get_performance_stats()
        if p.memory.cache:
            stats['cache'] = p.memory.cache.get_stats()
        return stats

    baseline = run_variant(use_cache=False)

    variants = []
    for size in COMPARE_SIZES:
        for ways in COMPARE_WAYS:
            for policy in COMPARE_POLICIES:
                stats = run_variant(use_cache=True, cache_size=size,
                                    associativity=ways, write_policy=policy)
                variants.append({
                    'size': size,
                    'associativity': ways,
                    'write_policy': policy,
                    'stats': stats,
                })

    return {'baseline': baseline, 'variants': variants}


@app.delete("/session/{sid}")
def delete_session(sid: str):
    if sid not in sessions:
        raise HTTPException(status_code=404, detail="session negasita")
    del sessions[sid]
    return {"deleted": sid}
