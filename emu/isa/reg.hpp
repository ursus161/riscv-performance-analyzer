#pragma once
#include <cstdint>

namespace emu::reg {

// abi reg names for risc-v architecture
// convert to register indices directly: cpu.reg(reg::a0).
enum : std::uint8_t {
    zero, ra, sp, gp, tp, t0, t1, t2,
    s0, s1, a0, a1, a2, a3, a4, a5,
    a6, a7, s2, s3, s4, s5, s6, s7,
    s8, s9, s10, s11, t3, t4, t5, t6,
};

} // namespace emu::reg