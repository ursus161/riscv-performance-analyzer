#pragma once
#include <bit>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <expected>
#include <vector>

namespace emu {

// risc-v is little-endian; copying bytes straight through is only correct on a
// little-endian host (x86-64, most ARM)
// fail the build otherwise, this case really isnt going to happen unless we re on very old hardware
static_assert(std::endian::native == std::endian::little, "host must be little-endian");

enum class MemFault : std::uint8_t { OutOfBounds }; // ill add more later

// accessible widths: 8/16/32-bit unsigned.
template <typename T>
concept MemWord = std::same_as<T, std::uint8_t> || std::same_as<T, std::uint16_t> ||
                  std::same_as<T, std::uint32_t>;

// flat RAM mapped at [base, base + size).
class Memory {
public:
    Memory(std::uint32_t base, std::size_t size) : base_(base), data_(size, 0) {}

    template <MemWord T>
    std::expected<T, MemFault> load(std::uint32_t addr) const {

        auto off = offset(addr, sizeof(T));
        if (!off) return std::unexpected(off.error());

        T value;
        std::memcpy(&value, data_.data() + *off, sizeof(T)); // memcpy: safe for misaligned addrs


        return value;
    }

    template <MemWord T>
    std::expected<void, MemFault> store(std::uint32_t addr, T value) {
        
        auto off = offset(addr, sizeof(T));
        if (!off) return std::unexpected(off.error());
        
        std::memcpy(data_.data() + *off, &value, sizeof(T));
        return {};
    }

    std::uint32_t base() const { return base_; }
    std::size_t size() const { return data_.size(); }

private:
    // translate a guest addr to an index into data_, checking the whole access fits.
    std::expected<std::size_t, MemFault> offset(std::uint32_t addr, std::size_t width) const {
        if (addr < base_) return std::unexpected(MemFault::OutOfBounds);
        std::size_t off = addr - base_;
        if (off + width > data_.size()) return std::unexpected(MemFault::OutOfBounds);
        return off;
    }

    std::uint32_t base_;
    std::vector<std::uint8_t> data_;
};

} // namespace emu