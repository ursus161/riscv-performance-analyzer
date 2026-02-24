import sys
from core.parser import parse_assembly
from pipeline.controller import Pipeline
from core.cache import Cache


def print_usage():
    print("Usage: python simulator.py <file.s> [options]")
    print("\nOptions:")
    print("  --cache         Enable cache simulation")
    print("  --cache-size N  Cache size in bytes (default: 256)")
    print("  --associativity N  N-way associativity (default: 2)")
    print("\nExample:")
    print("  python simulator.py programs/test.s")
    print("  python simulator.py programs/test.s --cache --cache-size 512")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    filename = sys.argv[1]
    use_cache = '--cache' in sys.argv
    tutoriat_mode = '--tutoriat' in sys.argv
    be_verbose = '--verbose' in sys.argv

    cache_size = 256
    associativity = 2

    for i, arg in enumerate(sys.argv):
        if arg == '--cache-size' and i + 1 < len(sys.argv):
            cache_size = int(sys.argv[i + 1])
        if arg == '--associativity' and i + 1 < len(sys.argv):
            associativity = int(sys.argv[i + 1])

    try:
        instructions = parse_assembly(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return
    except Exception as e:
        print(f"Error parsing file: {e}")
        return

    print(f"Loaded {len(instructions)} instructions\n")

    if use_cache:
        write_policy = 'write-back' if '--write-back' in sys.argv else 'write-through'

        print(f"Cache configuration: {cache_size}B, {associativity}-way")
        cache = Cache(size=cache_size, line_size=16, associativity=associativity, write_policy=write_policy)
        pipeline = Pipeline(instructions, cache=cache, verbose=be_verbose)
    else:
        pipeline = Pipeline(instructions, verbose=be_verbose)

    pipeline.run()

    print("\n" + "=" * 50)
    print("  Performance Results")
    print("=" * 50)

    stats = pipeline.get_performance_stats()
    print(f"\nExecution:")
    print(f"  Total cycles:     {stats['total_cycles']}")
    print(f"  Instructions:     {stats['total_instructions']}")
    print(f"  CPI:              {stats['cpi']:.2f}")
    print(f"  IPC:              {stats['ipc']:.2f}")

    print(f"\nRegisters:")
    for i in range(1, 8):
        val = pipeline.registers.read(i)
        if val != 0:
            print(f"  x{i} = {val}")

    if use_cache:
        cache_stats = cache.get_stats()
        mem_stats = pipeline.memory.get_stats()

        print(f"\nCache Performance:")
        print(f"  Hit rate:         {cache_stats['hit_rate'] * 100:.1f}%")
        print(f"  Hits:             {cache_stats['hits']}")
        print(f"  Misses:           {cache_stats['misses']}")
        print(f"  AMAT:             {cache_stats['amat']:.2f} cycles")
        print(f"\nMemory:")
        print(f"  Total latency:    {mem_stats['total_latency']} cycles")
        print(f"  RAM accesses:     {mem_stats['ram_accesses']}")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()