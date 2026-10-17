#pragma once
#include <expected>

#include "../isa/isa.hpp"
#include "../machine.hpp"
#include "trap.hpp"

namespace emu {

std::expected<void, Trap> execute(Machine& m, const Instruction& in);

} // namespace emu
