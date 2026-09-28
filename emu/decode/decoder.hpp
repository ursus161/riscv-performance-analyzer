#pragma once
#include <cstdint>

#include "isa/isa.hpp"

namespace emu {
    
// immediate extraction per insturction format


constexpr std::int32_t imm_i(std::uint32_t raw) {
    return static_cast<std::int32_t>(raw) >> 20;
}

constexpr std::int32_t imm_s(std::uint32_t raw) {
    return static_cast<std::int32_t>(
        static_cast<std::uint32_t>(static_cast<std::int32_t>(raw & 0xfe000000) >> 20)
        | ((raw >> 7) & 0x1f));
}

// B-type: imm[12|10:5] in bits 31:25, imm[4:1|11] in bits 11:7; imm[0] is 0
constexpr std::int32_t imm_b(std::uint32_t raw) {
    return static_cast<std::int32_t>(
        static_cast<std::uint32_t>(static_cast<std::int32_t>(raw & 0x80000000) >> 19)
        | ((raw << 4)  & 0x800)
        | ((raw >> 20) & 0x7e0)
        | ((raw >> 7)  & 0x1e));
}

constexpr std::int32_t imm_u(std::uint32_t raw) {
    return static_cast<std::int32_t>(raw & 0xfffff000);
}

// J-type: imm[20|10:1|11|19:12] in bits 31:12; imm[0] is 0.
constexpr std::int32_t imm_j(std::uint32_t raw) {
    return static_cast<std::int32_t>(
        static_cast<std::uint32_t>(static_cast<std::int32_t>(raw & 0x80000000) >> 11)
        | (raw & 0xff000)
        | ((raw >> 9)  & 0x800)
        | ((raw >> 20) & 0x7fe));
}

static_assert(imm_i(0xfff00093) == -1);          // addi x1, x0, -1
static_assert(imm_i(0x7ff00093) == 2047);        // addi x1, x0, 2047
static_assert(imm_s(0xfe000e23) == -4);          // sb x0, -4(x0)
static_assert(imm_s(0x00000423) == 8);           // sb x0, 8(x0)
static_assert(imm_b(0xfe000ee3) == -4);          // beq x0, x0, -4
static_assert(imm_b(0x00000463) == 8);           // beq x0, x0, 8
static_assert(imm_b(0x000000e3) == 2048);        // beq x0, x0, 2048 (imm[11] lives in bit 7)
static_assert(imm_u(0x123450b7) == 0x12345000);  // lui x1, 0x12345
static_assert(imm_u(0xfffff0b7) == -4096);       // lui x1, 0xfffff
static_assert(imm_j(0xffdff06f) == -4);          // jal x0, -4
static_assert(imm_j(0x0080006f) == 8);           // jal x0, 8
static_assert(imm_j(0x0010006f) == 2048);        // jal x0, 2048 (imm[11] lives in bit 20)

// decode a 32 bit instruction, unmatched encodings yield Op::INVALID
Instruction decode(std::uint32_t raw);

} // namespace emu
