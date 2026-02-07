from core.memory import Memory


def run():
    def test_valid_config():
        memory = Memory(size=1024)
        assert memory.size == 1024
        print("valid config test passed ")

    def test_invalid_size_type():
        try:
            Memory(size="1024")
        except TypeError as e:
            assert "must be int" in str(e)
            print(f"invalid size type correctly rejected: {e} ")
            return

        raise AssertionError("should raise TypeError for non-int size")

    def test_invalid_size_negative():
        try:
            Memory(size=-1024)
        except ValueError as e:
            assert "must be positive" in str(e)
            print(f"negative size correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for negative size")

    def test_invalid_size_alignment():
        try:
            Memory(size=1023)
        except ValueError as e:
            assert "multiple of 4" in str(e)
            print(f"unaligned size correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for unaligned size")

    def test_aligned_read():
        memory = Memory(size=1024)
        memory.write(0x100, 42)
        value = memory.read(0x100)
        assert value == 42
        print("aligned read test passed ")

    def test_unaligned_read():
        memory = Memory(size=1024)

        try:
            memory.read(0x101)
        except ValueError as e:
            assert "unaligned" in str(e)
            print(f"unaligned read correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for unaligned read")

    def test_unaligned_write():
        memory = Memory(size=1024)

        try:
            memory.write(0x102, 42)
        except ValueError as e:
            assert "unaligned" in str(e)
            print(f"unaligned write correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for unaligned write")

    def test_out_of_bounds_read():
        memory = Memory(size=1024)

        try:
            memory.read(0x1000)
        except ValueError as e:
            assert "out of bounds" in str(e)
            print(f"out of bounds read correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for out of bounds read")

    def test_out_of_bounds_write():
        memory = Memory(size=1024)

        try:
            memory.write(0x1000, 42)
        except ValueError as e:
            assert "out of bounds" in str(e)
            print(f"out of bounds write correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for out of bounds write")

    def test_negative_address():
        memory = Memory(size=1024)

        try:
            memory.read(-4)
        except ValueError as e:
            assert "non-negative" in str(e)
            print(f"negative address correctly rejected: {e} ")
            return

        raise AssertionError("should raise ValueError for negative address")

    def test_boundary_addresses():
        memory = Memory(size=1024)

        for addr in [0x0, 0x4, 0x8, 0x100, 0x200]:
            memory.write(addr, addr)
            assert memory.read(addr) == addr

        print("boundary addresses test passed ")

    test_valid_config()
    test_invalid_size_type()
    test_invalid_size_negative()
    test_invalid_size_alignment()
    test_aligned_read()
    test_unaligned_read()
    test_unaligned_write()
    test_out_of_bounds_read()
    test_out_of_bounds_write()
    test_negative_address()
    test_boundary_addresses()


if __name__ == "__main__":
    try:
        run()
        print("\nall memory validation tests passed ")
    except AssertionError as e:
        print(f"test failed: {e}")