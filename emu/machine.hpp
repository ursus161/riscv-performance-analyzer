#pragma once
#include "cpu/cpu.hpp"
#include "mem/memory.hpp"

namespace emu {

struct Machine {
    Cpu cpu;
    Memory mem;
};

} // namespace emu
