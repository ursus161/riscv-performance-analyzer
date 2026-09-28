#pragma once
#include <cstdint>

namespace emu {

// values match the RISC-V mcause exception codes.
// just a subset of the codes are implemented here, but more can be added later.
enum class TrapCause : std::uint8_t {
    InstrMisaligned = 0, InstrAccessFault = 1, IllegalInstr = 2, Breakpoint = 3,
    LoadMisaligned = 4, LoadAccessFault = 5, StoreMisaligned = 6, StoreAccessFault = 7, 
    ECallU = 8, ECallM = 11, 
    PageFaultInstr = 12, PageFaultLoad = 13, PageFaultStore = 15
};

struct Trap {
    TrapCause cause;
    std::uint32_t tval;   // faulting address, or 0 if not applicable
};

} // namespace emu
