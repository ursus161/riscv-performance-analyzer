#pragma once
#include <array>
#include <cstdint>

#include "isa.hpp"

namespace emu {

struct InstrSpecifications {
    std::uint32_t mask;
    std::uint32_t match;
    Op op;
    Format fmt;
    const char* name;
};

inline constexpr std::array<InstrSpecifications, 40> kRV32I = {{
    // upper immediate / jumps
    {0x0000007f, 0x00000037, Op::LUI,    Format::U, "lui"},
    {0x0000007f, 0x00000017, Op::AUIPC,  Format::U, "auipc"},
    {0x0000007f, 0x0000006f, Op::JAL,    Format::J, "jal"},
    {0x0000707f, 0x00000067, Op::JALR,   Format::I, "jalr"},

    // branches
    {0x0000707f, 0x00000063, Op::BEQ,    Format::B, "beq"},
    {0x0000707f, 0x00001063, Op::BNE,    Format::B, "bne"},
    {0x0000707f, 0x00004063, Op::BLT,    Format::B, "blt"},
    {0x0000707f, 0x00005063, Op::BGE,    Format::B, "bge"},
    {0x0000707f, 0x00006063, Op::BLTU,   Format::B, "bltu"},
    {0x0000707f, 0x00007063, Op::BGEU,   Format::B, "bgeu"},

    // loads
    {0x0000707f, 0x00000003, Op::LB,     Format::I, "lb"},
    {0x0000707f, 0x00001003, Op::LH,     Format::I, "lh"},
    {0x0000707f, 0x00002003, Op::LW,     Format::I, "lw"},
    {0x0000707f, 0x00004003, Op::LBU,    Format::I, "lbu"},
    {0x0000707f, 0x00005003, Op::LHU,    Format::I, "lhu"},

    // stores
    {0x0000707f, 0x00000023, Op::SB,     Format::S, "sb"},
    {0x0000707f, 0x00001023, Op::SH,     Format::S, "sh"},
    {0x0000707f, 0x00002023, Op::SW,     Format::S, "sw"},

    // op-imm
    {0x0000707f, 0x00000013, Op::ADDI,   Format::I, "addi"},
    {0x0000707f, 0x00002013, Op::SLTI,   Format::I, "slti"},
    {0x0000707f, 0x00003013, Op::SLTIU,  Format::I, "sltiu"},
    {0x0000707f, 0x00004013, Op::XORI,   Format::I, "xori"},
    {0x0000707f, 0x00006013, Op::ORI,    Format::I, "ori"},
    {0x0000707f, 0x00007013, Op::ANDI,   Format::I, "andi"},
    {0xfe00707f, 0x00001013, Op::SLLI,   Format::I, "slli"},
    {0xfe00707f, 0x00005013, Op::SRLI,   Format::I, "srli"},
    {0xfe00707f, 0x40005013, Op::SRAI,   Format::I, "srai"},

    // op
    {0xfe00707f, 0x00000033, Op::ADD,    Format::R, "add"},
    {0xfe00707f, 0x40000033, Op::SUB,    Format::R, "sub"},
    {0xfe00707f, 0x00001033, Op::SLL,    Format::R, "sll"},
    {0xfe00707f, 0x00002033, Op::SLT,    Format::R, "slt"},
    {0xfe00707f, 0x00003033, Op::SLTU,   Format::R, "sltu"},
    {0xfe00707f, 0x00004033, Op::XOR,    Format::R, "xor"},
    {0xfe00707f, 0x00005033, Op::SRL,    Format::R, "srl"},
    {0xfe00707f, 0x40005033, Op::SRA,    Format::R, "sra"},
    {0xfe00707f, 0x00006033, Op::OR,     Format::R, "or"},
    {0xfe00707f, 0x00007033, Op::AND,    Format::R, "and"},

    // system
    {0x0000707f, 0x0000000f, Op::FENCE,  Format::I, "fence"},
    {0xffffffff, 0x00000073, Op::ECALL,  Format::I, "ecall"},
    {0xffffffff, 0x00100073, Op::EBREAK, Format::I, "ebreak"},
}};

}  