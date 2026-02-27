import sys
import copy
from core.parser import parse_assembly
from pipeline.controller import Pipeline
from core.cache import Cache


def compare_caches(filename):

    try:
        instructions  = parse_assembly(filename)
        data_segment = {}
    except Exception as e:
        print(f"Error: {e}")
        return

    configs = [
        {"size": 64, "assoc": 1, "name": "64B direct-mapped"},
        {"size": 128, "assoc": 1, "name": "128B direct-mapped"},
        {"size": 128, "assoc": 2, "name": "128B 2-way"},
        {"size": 256, "assoc": 2, "name": "256B 2-way"},
        {"size": 512, "assoc": 2, "name": "512B 2-way"},
        {"size": 512, "assoc": 4, "name": "512B 4-way"},
    ]

    print(f"\n{'=' * 70}")
    print(f"  CACHE CONFIGURATION COMPARISON")
    print(f"{'=' * 70}")
    print(f"\nProgram: {filename}")
    print(f"Instructions: {len(instructions)}")
    if data_segment:
        print(f"Data segment: {len(data_segment)} words")
    print(f"\nTesting {len(configs)} cache configurations...\n")


    print(f"{'Configuration':<25} {'Hit Rate':<12} {'Latency':<12} {'Speedup':<10} {'AMAT'}")
    print("-" * 70)

    baseline_latency = None
    results = []

    for config in configs:

        cache = Cache(
            size=config['size'],
            line_size=16,
            associativity=config['assoc'],
            write_policy='write-back'
        )

        instr_copy = copy.deepcopy(instructions)
        pipeline = Pipeline(instr_copy, cache=cache, verbose=False)

        for address, value in data_segment.items():
            pipeline.memory.write(address, value)

        pipeline.run()

        cache_stats = cache.get_stats()
        mem_stats = pipeline.memory.get_stats()

        if baseline_latency is None:
            baseline_latency = mem_stats['total_latency']
            speedup_str = "baseline"
        else:
            speedup = baseline_latency / mem_stats['total_latency']
            speedup_str = f"{speedup:.2f}×"

        # Store results
        results.append({
            'config': config,
            'hit_rate': cache_stats['hit_rate'],
            'latency': mem_stats['total_latency'],
            'amat': cache_stats['amat'],
            'speedup': speedup_str
        })


        print(f"{config['name']:<25} {cache_stats['hit_rate'] * 100:>6.1f}%     "
              f"{mem_stats['total_latency']:>6} cy    {speedup_str:>8}   "
              f"{cache_stats['amat']:>6.2f} cy")

    # Analysis
    print(f"\n{'=' * 70}")
    print("  ANALYSIS")
    print(f"{'=' * 70}\n")

    #  best config
    best_by_hit_rate = max(results, key=lambda x: x['hit_rate'])
    best_by_speedup = max(results, key=lambda x: float(x['speedup'].rstrip('×')) if x['speedup'] != 'baseline' else 0)

    print(f"Best hit rate:  {best_by_hit_rate['config']['name']} ({best_by_hit_rate['hit_rate'] * 100:.1f}%)")
    if best_by_speedup['speedup'] != 'baseline':
        print(f"Best speedup:   {best_by_speedup['config']['name']} ({best_by_speedup['speedup']})")


    print(f"\nRECOMMENDATIONS:")

    # sweet spot , cumva cea mai buna alegere s ar afla aici
    for i, result in enumerate(results):
        if i > 0:
            prev = results[i - 1]
            hit_improvement = (result['hit_rate'] - prev['hit_rate']) * 100

            if hit_improvement < 5:  # devine deja inutil
                print(f" {prev['config']['name']}: Best cost/performance ratio")
                print(f" (Beyond this, little improvement for the cost)")
                break

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 cache_compare.py <file.s>")
        sys.exit(1)

    compare_caches(sys.argv[1])