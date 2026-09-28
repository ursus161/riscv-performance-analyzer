#pragma once
#include "../cpu/cpu.hpp"
#include "../isa/isa.hpp"

namespace emu {

void execute(Cpu& cpu, const Instruction& in);

} // namespace emu