#include "exec/execute.hpp"


namespace emu{


void execute(Cpu& cpu, const Instruction& in) {

    std::uint32_t a = cpu.reg(in.rs1);
    std::uint32_t b = cpu.reg(in.rs2);
    std::uint32_t next_pc = cpu.pc + 4;   // next instruction

    switch (in.op) {
        case Op::ADD: cpu.set_reg(in.rd, a + b); break;
        case Op::SUB: cpu.set_reg(in.rd, a - b); break;
        case Op::SLL: cpu.set_reg(in.rd, a << (b & 0x1f)); break;
        case Op::SLT: cpu.set_reg(in.rd, static_cast<std::int32_t>(a) < static_cast<std::int32_t>(b)); break;
        case Op::SLTU: cpu.set_reg(in.rd, a < b ? 1 : 0); break;
        case Op::XOR: cpu.set_reg(in.rd, a ^ b); break;
        case Op::SRL: cpu.set_reg(in.rd, a >> (b & 0x1f)); break;
        case Op::SRA: cpu.set_reg(in.rd, static_cast<std::uint32_t>(static_cast<std::int32_t>(a) >> (b & 0x1f))); break;
        case Op::OR: cpu.set_reg(in.rd, a | b); break;
        case Op::AND: cpu.set_reg(in.rd, a & b); break;

        default: break;
    }

    cpu.pc = next_pc;
}


};