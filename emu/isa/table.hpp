#pragma once
#include <cstdint>
#include "emu/isa/isa.hpp"

struct InstrSpecifications {

    std::uint32_t mask;
    std::uint32_t match;
    emu::Op op;
    emu::Format fmt;
    const char* name;

};