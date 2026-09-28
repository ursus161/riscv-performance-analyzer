#include "decode/decoder.hpp"
#include "isa/table.hpp"

namespace emu {

namespace {

constexpr std::uint8_t rd(std::uint32_t raw)  { return (raw >> 7)  & 0x1f; }
constexpr std::uint8_t rs1(std::uint32_t raw) { return (raw >> 15) & 0x1f; }
constexpr std::uint8_t rs2(std::uint32_t raw) { return (raw >> 20) & 0x1f; }

} // namespace

Instruction decode(std::uint32_t raw) {
    for (const auto& spec : kRV32I) {
        if ((raw & spec.mask) != spec.match) continue; //that was the point of the table format 

       
        Instruction inst{spec.op, 0, 0, 0, 0};
        switch (spec.fmt) {
            case Format::R: inst.rd = rd(raw); inst.rs1 = rs1(raw); inst.rs2 = rs2(raw); break;
            case Format::I: inst.rd = rd(raw); inst.rs1 = rs1(raw); inst.imm = imm_i(raw); break;
            case Format::S: inst.rs1 = rs1(raw); inst.rs2 = rs2(raw); inst.imm = imm_s(raw); break;
            case Format::B: inst.rs1 = rs1(raw); inst.rs2 = rs2(raw); inst.imm = imm_b(raw); break;
            case Format::U: inst.rd = rd(raw); inst.imm = imm_u(raw); break;
            case Format::J: inst.rd = rd(raw); inst.imm = imm_j(raw); break;
        }
 
        if (spec.op == Op::SLLI || spec.op == Op::SRLI || spec.op == Op::SRAI)
            inst.imm &= 0x1f;

        return inst;
    }
    return {Op::INVALID, 0, 0, 0, 0}; // unmatched encoding that can be handled later by something like a illegal instruction fault
}  

} // namespace emu
