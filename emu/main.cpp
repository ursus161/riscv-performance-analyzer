#include <cstdio>

#include "decode/decoder.hpp"
#include "exec/execute.hpp"

using namespace emu;

int main() {
    Machine m{Cpu{}, Memory{0x80000000, 4096}};

    // sum 1..10 into a0, then ecall
    const std::uint32_t program[] = {
        0x00000513,  // addi a0, x0, 0      a0 = 0
        0x00100293,  // addi t0, x0, 1      t0 = 1
        0x00b00313,  // addi t1, x0, 11     t1 = 11
        0x00550533,  // add  a0, a0, t0     a0 += t0       
        0x00128293,  // addi t0, t0, 1      t0++
        0xfe629ce3,  // bne  t0, t1, -8     if t0 != 11 goto loop, could use a branch predictor later here 
        0x00000073,  // ecall
    };

    for (std::uint32_t i = 0; i < std::size(program); ++i)
        (void)m.mem.store<std::uint32_t>(0x80000000 + 4 * i, program[i]);
    m.cpu.pc = 0x80000000;

    for (int steps = 0; steps < 1000; ++steps) {
        auto word = m.mem.load<std::uint32_t>(m.cpu.pc);   // fetch
        if (!word) [[unlikely]] { std::puts("fetch fault"); return 1; } // trusting myself :) marking it as unsafe for the smarter than me bp to optimize

        auto result = execute(m, decode(*word));            // decode + execute
        if (!result) [[unlikely]] { // same
            std::printf("trap %d at pc=0x%08x, a0=%u\n",
                        static_cast<int>(result.error().cause), m.cpu.pc, m.cpu.reg(10)); //10th reg is obv t10
            return 0;
        }
    }
    std::puts("step limit reached");
}