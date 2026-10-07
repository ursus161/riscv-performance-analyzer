#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest/doctest.h>

#include "decode/decoder.hpp"
#include "exec/execute.hpp"
#include "isa/reg.hpp"

using namespace emu;

namespace {

constexpr std::uint32_t kRamBase = 0x80000000;

Machine make_machine() {
    Machine m{Cpu{}, Memory{kRamBase, 4096}};
    m.cpu.pc = kRamBase;
    return m;
}

// Decode and execute one raw instruction word.
auto exec(Machine& m, std::uint32_t raw) { return execute(m, decode(raw)); }

} // namespace

TEST_CASE("ADD adds two registers and advances pc") {
    Machine m = make_machine();
    m.cpu.set_reg(reg::t1, 5);
    m.cpu.set_reg(reg::t2, 7);

    REQUIRE(exec(m, 0x007302b3));  // add t0, t1, t2

    CHECK(m.cpu.reg(reg::t0) == 12);
    CHECK(m.cpu.pc == kRamBase + 4);
}

TEST_CASE("ADD wraps around on overflow") {
    Machine m = make_machine();
    m.cpu.set_reg(reg::t1, 0xffffffff);
    m.cpu.set_reg(reg::t2, 1);

    REQUIRE(exec(m, 0x007302b3));  // add t0, t1, t2

    CHECK(m.cpu.reg(reg::t0) == 0);
}

TEST_CASE("writes to x0 are discarded") {
    Machine m = make_machine();
    m.cpu.set_reg(reg::t1, 5);
    m.cpu.set_reg(reg::t2, 7);

    REQUIRE(exec(m, 0x00730033));  // add x0, t1, t2

    CHECK(m.cpu.reg(reg::zero) == 0);
}