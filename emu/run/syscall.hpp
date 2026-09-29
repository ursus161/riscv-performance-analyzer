#pragma once
#include <cstdint>

#include "machine.hpp"

namespace emu {

// syscall numbers as defined by the Linux kernel for RISC-V
// (include/uapi/asm-generic/unistd.h). only the implemented ones are listed.
enum class Syscall : std::uint32_t {
    Write = 64,
    Exit = 93,
    ExitGroup = 94,
};

// guest errno values (include/uapi/asm-generic/errno-base.h, errno.h).
// kept explicit instead of <cerrno>: those are the host's values, not the guest's.
namespace guest_errno {
inline constexpr std::int32_t EBADF = 9; //bad file descriptor
inline constexpr std::int32_t EFAULT = 14; // bad address, out of process scope
inline constexpr std::int32_t ENOSYS = 38; // syscall not implemented
} // namespace guest_errno

enum class SyscallOutcome : std::uint8_t {
    Continue,  // result is in a0, execution resumes after the ecall
    Exit,      // guest asked to terminate, exit code in a0
};

// linux calling convention: number in a7, arguments in a0..a5, result in a0.
// like the kernel, errors are reported to the guest as -errno in a0.
SyscallOutcome handle_syscall(Machine& m);

} // namespace emu