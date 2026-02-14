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

    def _validate_address(self, address):

        if not isinstance(address, int):
            raise TypeError(f"Adresa trebuie sa fie int, nu {type(address).__name__}")

        if address % 4 != 0:
            raise ValueError(f"Adresa unaligned: {address:#x} (trebuie 4-byte aligned)")

        if address >= self.size:
            raise ValueError(f"Adresa out of bounds: {address:#x} (marime memorie: {self.size:#x})")

    def read(self, address):
        self._validate_address(address)
            
        if self.cache: #in cazul in care testez fara cache, nu mi intra aici
            hit, latency = self.cache.access(address, is_write=False)
            self.total_latency += latency
            if not hit:
                self.ram_accesses += 1
        else:
            self.total_latency += 50
            self.ram_accesses += 1

        word_address = address >> 2
        return self.data[word_address]

    def write(self, address, value):

        if self.cache:
            hit, latency = self.cache.access(address, is_write=True)
            self.total_latency += latency
            if not hit:
                self.ram_accesses += 1
        else:
            self.total_latency += 50
            self.ram_accesses += 1

        word_address = address >> 2
        self.data[word_address] = value

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
    assert mem.read(0x200) == 0x100
    print(mem)
