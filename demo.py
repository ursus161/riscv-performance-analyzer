import copy

from pipeline.controller import Pipeline
from core.instruction import Instruction
from core.cache import Cache
import programs.listadd as listadd


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title):
    print(f"\n--- {title} ---")


def demo_simple_execution():

    print_header("DEMO 1: Basic Instruction Execution")

    print("\nProgram:")
    print("  addi x1, x0, 10    # x1 = 10")
    print("  addi x2, x0, 20    # x2 = 20")
    print("  add  x3, x1, x2    # x3 = x1 + x2 = 30")

    instructions = [
        Instruction("addi", rd=1, rs1=0, imm=10),
        Instruction("addi", rd=2, rs1=0, imm=20),
        Instruction("add", rd=3, rs1=1, rs2=2),
    ]

    pipeline = Pipeline(instructions)
    pipeline.run()

    print_section("Results")
    print(f"  x1 = {pipeline.registers.read(1)}")
    print(f"  x2 = {pipeline.registers.read(2)}")
    print(f"  x3 = {pipeline.registers.read(3)}")
    print(f"  Total cycles: {pipeline.cycle}")
    print(f"  CPI: {pipeline.cycle / 3:.2f}")


def demo_cache_impact():

    print_header("DEMO 2: Cache Performance Impact")

    print("\nProgram: Array sum (spatial locality test)")
    print("  values = [10, 20, 30, 40]")
    print("  sum = 0")
    print("  for v in values:")
    print("      sum += v")

    # Without cache
    print_section("WITHOUT Cache")
    pipeline_no_cache = Pipeline(listadd.get_program())
    pipeline_no_cache.run()

    stats_no_cache = pipeline_no_cache.get_performance_stats()
    mem_stats_no_cache = pipeline_no_cache.memory.get_stats()

    print(f"  Cycles: {stats_no_cache['total_cycles']}")
    print(f"  Result (x3): {pipeline_no_cache.registers.read(3)}")
    print(f"  Memory latency: {mem_stats_no_cache['total_latency']} cycles")
    print(f"  RAM accesses: {mem_stats_no_cache['ram_accesses']}")

    # with cache
    print_section("WITH Cache (2-way, 256B, LRU)")
    cache = Cache(size=256, line_size=16, associativity=2, write_policy='write-back')
    pipeline_cache = Pipeline(listadd.get_program(), cache=cache)
    pipeline_cache.run()

    stats_cache = pipeline_cache.get_performance_stats()
    mem_stats_cache = pipeline_cache.memory.get_stats()
    cache_stats = cache.get_stats()

    print(f"  Cycles: {stats_cache['total_cycles']}")
    print(f"  Result (x3): {pipeline_cache.registers.read(3)}")
    print(f"  Memory latency: {mem_stats_cache['total_latency']} cycles")
    print(f"  Cache hit rate: {cache_stats['hit_rate'] * 100:.1f}%")
    print(f"  Cache misses: {cache_stats['misses']}")
    print(f"  Cache hits: {cache_stats['hits']}")

    # comparatie
    print_section("Performance Comparison")
    speedup = mem_stats_no_cache['total_latency'] / mem_stats_cache['total_latency']
    latency_reduction = mem_stats_no_cache['total_latency'] - mem_stats_cache['total_latency']

    print(f"  Speedup: {speedup:.2f}×")
    print(
        f"  Latency reduction: {latency_reduction} cycles ({latency_reduction / mem_stats_no_cache['total_latency'] * 100:.1f}%)")
    print(f"  Cache effectiveness: {cache_stats['hit_rate'] * 100:.1f}% hits → spatial locality working!")


def demo_hazard_handling():

    print_header("DEMO 3: Hazard Detection & Data Forwarding")

    print("\nProgram (with data hazard):")
    print("  add  x5, x3, x4    # x5 = x3 + x4")
    print("  addi x6, x5, 10    # x6 = x5 + 10 (needs x5!)")
    print("  add  x7, x6, x5    # x7 = x6 + x5 (needs both!)")

    instructions = [
        Instruction("addi", rd=3, rs1=0, imm=10),
        Instruction("addi", rd=4, rs1=0, imm=20),
        Instruction("add", rd=5, rs1=3, rs2=4),
        Instruction("addi", rd=6, rs1=5, imm=10),
        Instruction("add", rd=7, rs1=6, rs2=5),
    ]

    pipeline = Pipeline(instructions)
    pipeline.run()

    print_section("Results")
    print(f"  x3 = {pipeline.registers.read(3)}")
    print(f"  x4 = {pipeline.registers.read(4)}")
    print(f"  x5 = {pipeline.registers.read(5)} (= x3 + x4 = 30)")
    print(f"  x6 = {pipeline.registers.read(6)} (= x5 + 10 = 40)")
    print(f"  x7 = {pipeline.registers.read(7)} (= x6 + x5 = 70)")
    print(f"\n  Total cycles: {pipeline.cycle}")
    print(f"  Forwarding enabled → no extra stalls needed ")


def demo_configuration_comparison():

    print_header("DEMO 4: Cache Configuration Impact")

    configs = [
        {"size": 64, "associativity": 1, "name": "64B direct-mapped"},
        {"size": 256, "associativity": 1, "name": "256B direct-mapped"},
        {"size": 256, "associativity": 2, "name": "256B 2-way"},
        {"size": 256, "associativity": 4, "name": "256B 4-way"},
        {"size": 512, "associativity": 1, "name": "512B direct-mapped"},
        {"size": 512, "associativity": 2, "name": "512B 2-way"},
        {"size": 512, "associativity": 4, "name": "512B 4-way"},
        {"size": 1024, "associativity": 4, "name": "1KB 4-way"},
    ]

    print("\nTesting configurations on array sum benchmark:")
    print(f"{'Configuration':<25} {'Hit Rate':<12} {'Latency':<10} {'Speedup'}")
    print("-" * 60)

    baseline_latency = None
    l=[]
    for config in configs:
        print(config)
        cache = Cache(
            size=config['size'],
            line_size=16,
            associativity=config['associativity'],
            write_policy='write-back'
        )
        instructions = copy.deepcopy(listadd.get_program())
        pipeline = Pipeline(instructions, cache=cache)
        pipeline.run()

        cache_stats = cache.get_stats()
        mem_stats = pipeline.memory.get_stats()

        if baseline_latency is None:
            baseline_latency = mem_stats['total_latency']
            speedup_str ="1.0"
        else:
            speedup = baseline_latency / mem_stats['total_latency']
            speedup_str = f"{speedup:.1f}"
        l.append(f"{config['name']:<25} {cache_stats['hit_rate'] * 100:>6.1f}%  hitrate   {mem_stats['total_latency']:>6} cycles   {speedup_str:>8}x speedup")
        with open('demo_results.txt', 'w') as f:
            f.write("\n".join(l))


def main():
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  RISC-V CPU Simulator - Demo".center(58) + "█")
    print("█" + "  Pipeline + Cache + Performance Analysis".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)

    demo_simple_execution()
    input("\n[Press Enter to continue...]")

    demo_cache_impact()
    input("\n[Press Enter to continue...]")

    demo_hazard_handling()
    input("\n[Press Enter to continue...]")


    demo_configuration_comparison()
    input("\n[Press Enter to continue...]")

    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("    Pipeline executes instructions efficiently")
    print("    Cache provides 6-8× speedup on realistic workloads")
    print("    Data forwarding eliminates most stalls")
    print("    Configuration matters: larger + more associative = better")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()