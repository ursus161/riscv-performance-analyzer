#include "exec/execute.hpp"
#include "exec/trap.hpp"

namespace emu{


std::expected<void, Trap> execute(Machine& m, const Instruction& in) {

    Cpu& cpu = m.cpu; // machine's cpu

    std::uint32_t a = cpu.reg(in.rs1);
    std::uint32_t b = cpu.reg(in.rs2);
    std::uint32_t imm = static_cast<std::uint32_t>(in.imm); // immediate cast to uint for defined overflows unsigned arithmetic 
    std::uint32_t next_pc = cpu.pc + 4;   // next instruction
    bool taken = false;                   // set by branch instructions

    switch (in.op) {
        //cases for ALU operations
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
        //cases for immediate instructions
        case Op::ADDI: cpu.set_reg(in.rd, a + imm); break;
        case Op::SLTI: cpu.set_reg(in.rd, static_cast<std::int32_t>(a) < in.imm); break;
        case Op::SLTIU: cpu.set_reg(in.rd, a < imm ? 1 : 0); break;
        case Op::XORI: cpu.set_reg(in.rd, a ^ imm); break;
        case Op::ORI: cpu.set_reg(in.rd, a | imm); break;
        case Op::ANDI: cpu.set_reg(in.rd, a & imm); break;
        case Op::SLLI: cpu.set_reg(in.rd, a << imm); break;
        case Op::SRLI: cpu.set_reg(in.rd, a >> imm); break;
        case Op::SRAI: cpu.set_reg(in.rd, static_cast<std::uint32_t>(static_cast<std::int32_t>(a) >> imm)); break; 
        
        //cases for lui and auipc instructions
        case Op::LUI: cpu.set_reg(in.rd, imm); break;
        case Op::AUIPC: cpu.set_reg(in.rd, cpu.pc + imm); break;

        //cases for jump instructions
        // target is checked before rd/pc are written so a trap leaves state untouched
        case Op::JAL: {
            std::uint32_t target = cpu.pc + imm;
            // x&3 == 0 checks alignment which must be 4-bytes.
            // if the target address is misaligned, a trap is returned 
            if (target & 3) return std::unexpected(Trap{TrapCause::InstrMisaligned, target});
            cpu.set_reg(in.rd, next_pc); next_pc = target; break;
        }

        case Op::JALR: {
            std::uint32_t target = (a + imm) & ~1u;
            if (target & 3) return std::unexpected(Trap{TrapCause::InstrMisaligned, target});
            cpu.set_reg(in.rd, next_pc); next_pc = target; break;
        }

        //cases for branch instructions
        case Op::BEQ: taken = a == b; break;
        case Op::BNE: taken = a != b; break;
        case Op::BLT: taken = static_cast<std::int32_t>(a) < static_cast<std::int32_t>(b); break;
        case Op::BGE: taken = static_cast<std::int32_t>(a) >= static_cast<std::int32_t>(b); break;
        case Op::BLTU: taken = a < b; break;
        case Op::BGEU: taken = a >= b; break;

        case Op::FENCE: break;
        default: return std::unexpected(Trap{TrapCause::IllegalInstr, 0});
    }

    if (taken) {
        std::uint32_t target = cpu.pc + imm;
        if (target & 3) return std::unexpected(Trap{TrapCause::InstrMisaligned, target});
        next_pc = target;
    }

    cpu.pc = next_pc;
    return {};
}


}