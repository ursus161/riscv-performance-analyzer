#pragma once
#include <cstdint>
#include <expected>

#include "exec/trap.hpp"
#include "machine.hpp"

namespace emu {

enum class StopReason : std::uint8_t {
    Exit,       // guest called exit via ecall
    Trap,       // unhandled trap (illegal instruction, access fault etc)
    StepLimit,  // max_steps reached, likely an infinite loop? maybe i could handle it another way in the future
                // but given that the Halting Problem is undecidable, this is probably the best i can do for now
};

struct RunResult {
    StopReason reason;
    std::int32_t exit_code;  // valid when reason == Exit
    Trap trap;               // valid when reason == Trap
    std::uint64_t steps;     // instructions executed
};

// fetch, decode and execute ONE instruction. (the mem and wb stages are in the execute handler)
std::expected<void, Trap> step(Machine& m);

// Run until exit, an unhandled trap, or max_steps instructions.
RunResult run(Machine& m, std::uint64_t max_steps=0);

} // namespace emu