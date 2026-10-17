#pragma once
#include <cstdint>

namespace emu {

enum class Op : std::uint8_t {
    // upper immediate / jumps
    LUI, AUIPC, JAL, JALR,
    // branches
    BEQ, BNE, BLT, BGE, BLTU, BGEU,
    // loads
    LB, LH, LW, LBU, LHU,
    // stores
    SB, SH, SW,
    // op-imm
    ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI,
    // op
    ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND,
    // system
    FENCE, ECALL, EBREAK,
    INVALID
};

enum class Format : std::uint8_t { R, I, S, B, U, J }; // to be considered during instruction decoding 

struct Instruction {
    emu::Op op;
    std::uint8_t rd, rs1, rs2;
    std::int32_t imm; // imm can be signed 
};  

static_assert(sizeof(Instruction) == 8);

} // at first i didnt want to use a namespace but it seems like a good idea to avoid name collisions with other code files