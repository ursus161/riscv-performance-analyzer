#include <chrono>
#include <cstdio>
#include <iterator>

#include "isa/reg.hpp"
#include "run/run.hpp"

using namespace emu;

namespace {

constexpr std::uint32_t kRamBase = 0x80000000;

// Count to ~50M: ~100M instructions, long enough for a stable MIPS measurement.
constexpr std::uint32_t kBenchLoop[] = {
    0x00000293,  // addi t0, x0, 0
    0x02faf337,  // lui  t1, 0x2faf        t1 = 50,003,968
    0x00128293,  // addi t0, t0, 1         <- loop
    0xfe629ee3,  // bne  t0, t1, -4
    0x05d00893,  // addi a7, x0, 93        exit(a0)
    0x00000073,  // ecall
};

void load_program(Machine& m, const std::uint32_t* words, std::size_t count) {
    for (std::size_t i = 0; i < count; ++i)
        (void)m.mem.store<std::uint32_t>(kRamBase + 4 * static_cast<std::uint32_t>(i), words[i]);
    m.cpu.pc = kRamBase;
}

void report(const RunResult& r, const Machine& m, double seconds) {
    switch (r.reason) {
        case StopReason::Exit:
            std::printf("exit code %d\n", r.exit_code);
            break;
        case StopReason::Trap:
            std::printf("trap %d at pc=0x%08x\n", static_cast<int>(r.trap.cause), m.cpu.pc);
            break;
        case StopReason::StepLimit:
            std::puts("step limit reached");
            break;
    }
    std::printf("%lu instructions, %.3f s, %.1f MIPS\n",
                static_cast<unsigned long>(r.steps), seconds, r.steps / seconds / 1e6);
}

} // namespace

int main() {
    Machine m{Cpu{}, Memory{kRamBase, 4096}};
    load_program(m, kBenchLoop, std::size(kBenchLoop));

    auto t0 = std::chrono::steady_clock::now();
    RunResult r = run(m);
    auto t1 = std::chrono::steady_clock::now();

    report(r, m, std::chrono::duration<double>(t1 - t0).count());
}