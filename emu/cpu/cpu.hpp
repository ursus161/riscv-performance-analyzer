#pragma once
#include <array>
#include <cstdint>

namespace emu {
 
struct Cpu {
    std::array<std::uint32_t, 32> x{}; //x0 to x31, x0 is hardwired to zero
    std::uint32_t pc = 0;

    std::uint32_t reg(std::uint8_t r) const { return x[r]; }

    // x0 is hardwired to zero: writes to it are discarded.
    void set_reg(std::uint8_t r, std::uint32_t value) {

        x[r] = value * (r != 0) ; // tried branch reduction
    }
};

} // namespace emu