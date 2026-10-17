class Memory:

    # Reprezinta RAM-ul
    # Word-aligned (adresele sunt multipli de 4)
    # Adresele sunt in bytes, dar stocam words (32-bit)

    def __init__(self, size=2**16, cache=None):
        # size (int): nr de words / size=1024 → 4KB memorie

        self.size = size
        self.data = [0] * (size // 4)
        self.cache = cache
        self.ram_accesses = 0
        self.total_latency = 0

        self._validate_config()

    def _validate_config(self):

        if not isinstance(self.size, int):
            raise TypeError(f"Memory size-ul trebuie sa fie int, nu {type(self.size).__name__}")

        if self.size <= 0:
            raise ValueError(f"Memory size-ul trebuie sa fie pozitiv, dar este: {self.size}")

        if self.size % 4 != 0:
            raise ValueError(f"Memory size-ul trebuie sa fie multiplu de 4, dar este: {self.size}")

    def _validate_access(self, address, size):
        if not isinstance(address, int):
            raise TypeError(f"Adresa trebuie sa fie int, nu {type(address).__name__}")
        if address % size != 0:
            raise ValueError(f"Adresa unaligned: {address:#x} (trebuie {size}-byte aligned)")
        if address < 0 or address >= self.size:
            raise ValueError(f"Adresa out of bounds: {address:#x} (marime memorie: {self.size:#x})")

    def read(self, address, size=4):
        self._validate_access(address, size)
        shift = (address & (4 - size)) * 8
        mask = (1 << (size * 8)) - 1
        return (self.data[address >> 2] >> shift) & mask

    def write(self, address, value, size=4):
        self._validate_access(address, size)
        if size == 4:
            self.data[address >> 2] = value
            return
        idx = address >> 2
        shift = (address & (4 - size)) * 8
        mask = (1 << (size * 8)) - 1
        self.data[idx] = (self.data[idx] & ~(mask << shift)) | ((value & mask) << shift)

    def get_stats(self):
        return {
            'ram_accesses': self.ram_accesses,
            'total_latency': self.total_latency
        }

    def __str__(self):

        non_zero = {i * 4: v for i, v in enumerate(self.data) if v != 0}
        if not non_zero:
            return "Memoria e goala"
        return f"Memorie: {non_zero}"


if __name__ == "__main__":
    mem = Memory()
    mem.write(0x100,4)
    mem.write(0x200,4)
    assert mem.read(0x200) == 4
    print(mem)
