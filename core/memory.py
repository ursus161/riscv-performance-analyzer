class Memory:

    # Reprezinta RAM-ul
    # Word-aligned (adresele sunt multipli de 4)
    # Adresele sunt in bytes, dar stocam words (32-bit)

    def __init__(self, size=1024):

            # size (int): nr de words / size=1024 → 4KB memorie

        self.data = [0] * size

    def read(self, address):

        word_index = address >> 2  # address // 4
        return self.data[word_index]

    def write(self, address, value):

        word_index = address >> 2
        self.data[word_index] = value

    def __str__(self):

        non_zero = {i * 4: v for i, v in enumerate(self.data) if v != 0}
        if not non_zero:
            return "Memoria e goala"
        return f"Memorie: {non_zero}"


if __name__ == "__main__":
    mem = Memory(size=256)  # 256 words = 1KB

    # Test 1: Scriere
    mem.write(0, 42)
    mem.write(4, 100)
    mem.write(12, 255)

    # Test 2: Citire
    print(f"mem[0]:  {mem.read(0)}")  # 42
    print(f"mem[4]:  {mem.read(4)}")  # 100
    print(f"mem[12]: {mem.read(12)}")  # 255

    # Test 3: Afisare
    print(mem)  # Memorie: {0: 42, 4: 100, 12: 255}

    # Test 4: Suprascrie
    mem.write(4, 200)
    print(f"mem[4] dupa update: {mem.read(4)}")  # 200
