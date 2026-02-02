from pipeline.controller import Pipeline
from core.cache import Cache
from programs import listadd


def run_prog(cache):
    pipeline = Pipeline(listadd.get_program(), cache=cache)
    pipeline.run()

    result = {'cycles': pipeline.cycle,
              'regs': {x : pipeline.registers.read(x) for x in range(1, 32) if pipeline.registers.read(x) != 0},
              'cache': None if cache is None else cache.get_stats(),
              'memory': pipeline.memory.get_stats(),
              'cpi'  : pipeline.get_performance_stats()['cpi']
              }
    if cache:
        result['hit'] = cache.get_stats()['hit_rate']

    return result


def main():
    with open("test_rez.txt", "w") as g:
        r = run_prog(None)
        nocache_cycles = r['memory']['total_latency']  # aproximare
        g.write(f"no cache:\n\n"
                f"{r['cycles']} cycles\n"
                f"regs={r['regs']}\n"
                f"cpi:   {r['cpi']}\n"
                f"memory stats: {r['memory']}\n\n")

        cache = Cache(size=256, line_size=16, associativity=2)
        r = run_prog(cache)
        cache_cycles = r['memory']['total_latency']  # aproximare
        g.write(f"cache:\n\n"
                f"{r['cycles']} cycles\n"
                f"regs={r['regs']}, hit={r['hit'] * 100:.0f}%\n"
                f"memory stats: {r['memory']}\n"
                f"cpi:   {r['cpi']}\n"
                f"cache stats: {r['cache']}\n\n\n")

        g.write(f"folosind memoria cache ne miscam cu {round(((nocache_cycles-cache_cycles)/cache_cycles) * 100,2)}% "
                f"mai rapid\n\n"
                f"eficienta creste cu {round(((nocache_cycles-cache_cycles)/nocache_cycles) * 100,2)}%")


if __name__ == "__main__":
    main()