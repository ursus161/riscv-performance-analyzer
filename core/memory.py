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
    mem = Memory()
    mem.write(9,4)
    print(mem)
