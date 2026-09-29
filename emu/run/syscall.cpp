#include "run/syscall.hpp"

#include <cstdio>

#include "isa/reg.hpp"

namespace emu {

namespace {

// Returns bytes written, or -errno.
std::int32_t sys_write(Machine& m, std::uint32_t fd, std::uint32_t buf, std::uint32_t len) {
    
    std::FILE* out;
    switch (fd) {
        case 1: out = stdout; break;
        case 2: out = stderr; break;
        default: return -guest_errno::EBADF;
    }
        
    if (!out) [[unlikely]] return -guest_errno::EBADF;

    for (std::uint32_t i = 0; i < len; ++i) {
        auto byte = m.mem.load<std::uint8_t>(buf + i);
        if (!byte) [[unlikely]] return -guest_errno::EFAULT;  // buffer outside guest memory
        std::fputc(*byte, out);
    }
    return static_cast<std::int32_t>(len);
}

} // namespace

SyscallOutcome handle_syscall(Machine& m) {
    Cpu& cpu = m.cpu;
    std::int32_t result;

    switch (static_cast<Syscall>(cpu.reg(reg::a7))) { //a7 is the syscall number
        case Syscall::Exit:
            //handled by the run loop, which returns the exit code in a0.
        case Syscall::ExitGroup:
            return SyscallOutcome::Exit;

        case Syscall::Write:
            result = sys_write(m, cpu.reg(reg::a0), cpu.reg(reg::a1), cpu.reg(reg::a2));
            break;

        default:
            // unknown syscall: the kernel returns -ENOSYS and the program keeps running.
            std::fprintf(stderr, "[emu] unimplemented syscall %u\n", cpu.reg(reg::a7)); // a7 register holds the syscall number
            result = -guest_errno::ENOSYS;
            break;
    }

    cpu.set_reg(reg::a0, static_cast<std::uint32_t>(result));
    return SyscallOutcome::Continue;
}

} // namespace emu