import math

class CacheLine:

    def __init__(self):
        self.valid = False
        self.tag = 0
        self.data = None
        self.dirty = False
        self.lru_counter = 0  # pentru find_victim_lru

    def __repr__(self):
        if not self.valid:
            return "[gol]"
        dirty_mark = "*" if self.dirty else ""
        return f"[tag={self.tag:#x}{dirty_mark}]"


class Cache:

    def __init__(self, size=256, line_size=16, associativity=2,
                 write_policy='write-back'):
        self.size = size
        self.line_size = line_size
        self.associativity = associativity
        self.write_policy = write_policy


        self.num_lines = size // line_size
        self.num_sets = self.num_lines // associativity
        self._validate_data()

        self.offset_bits = (line_size - 1).bit_length() # daca am 32 biti --> 31 = 11111 in binar --> 5 biti
        self.index_bits = (self.num_sets - 1).bit_length() if self.num_sets > 1 else 0
        self.tag_bits = 32 - self.offset_bits - self.index_bits # restul


        # set = lista de n linii (n = policy ul: 2-way, 4-way, etc)
        self.sets = []
        for _ in range(self.num_sets):
            cache_set = []
            for _ in range(associativity):
                cache_set.append(CacheLine())
            self.sets.append(cache_set)

        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.write_backs = 0

    def _decode_address(self, address):

        offset_mask = (1 << self.offset_bits) - 1 # adica self.offset_bits de 1
        offset = address & offset_mask

        index_mask = (1 << self.index_bits) - 1
        index = (address >> self.offset_bits) & index_mask

        tag = address >> (self.offset_bits + self.index_bits) #doar restul

        return tag, index, offset

    def access(self, address, is_write=False):
        #daca nu e write e read, initializez is_write cu False pentru ca in cazul unei rulari gresite a metodei
        #read ul nu afecteaza cache ul
        tag, index, offset = self._decode_address(address)
        cache_set = self.sets[index]



        for way_idx, line in enumerate(cache_set):

            if line.valid and line.tag == tag: #hit

                self.hits += 1
                self._update_lru(cache_set, way_idx)

                if is_write:
                    if self.write_policy == 'write-back':
                        line.dirty = True
                        return (True, 1)  # write doar în cache && rescrierea se intampla la eviction
                    else:  # write-through
                        return (True, 1 + 50)   #+ram

                return (True, 1) #e read


        self.misses += 1
        victim_idx = self._find_lru_victim(cache_set)
        victim = cache_set[victim_idx]


        write_back_latency = 0
        if victim.valid and victim.dirty:
            self.write_backs += 1
            write_back_latency = 50

        if victim.valid:
            self.evictions += 1

        # load linie noua in victima
        victim.valid = True
        victim.tag = tag
        victim.dirty = is_write and (self.write_policy == 'write-back')
        self._update_lru(cache_set, victim_idx)

        #logica pt politica write-through, simpla dar ffff inceata
        #pt ca de fiecare data imi rescrie in RAM
        #A SE FOLOSI IN SISTEME SAFETY-CRITICAL ONLY
        if is_write and self.write_policy == 'write-through':

            return (False, 50+ 50 + write_back_latency)
        else:

            return (False, 50 + write_back_latency)

    def _find_lru_victim(self, cache_set):

        max_lru = -1
        victim_idx = 0

        for idx, line in enumerate(cache_set):
            if not line.valid:
                # nu trebuie eviction, prefer sa iau linia goala
                return idx

            if line.lru_counter > max_lru:
                max_lru = line.lru_counter
                victim_idx = idx

        return victim_idx

    def _update_lru(self, cache_set, accessed_idx):

        for line in cache_set:
            line.lru_counter += 1

        cache_set[accessed_idx].lru_counter = 0 #reset la linia curenta pt ca e cea mai noua

    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        miss_rate = 1 - hit_rate

        # AMAT = average memory access time = hit_time + miss_rate x miss_penalty
        hit_time = 1
        miss_penalty = 50  # timpul de acces la RAM
        amat = hit_time + miss_rate * miss_penalty

        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_accesses': total,
            'hit_rate': round(hit_rate, 2),
            'miss_rate': round(miss_rate, 2),
            'evictions': self.evictions,
            'write_backs': self.write_backs,
            'amat': round(amat, 2)
        }

    def _validate_data(self):
        if not math.log2(self.size).is_integer():
           raise ValueError("Cache size-ul mereu trebuie sa fie putere a lui 2")
        if not math.log2(self.line_size).is_integer():
           raise ValueError("Line size-ul mereu trebuie sa fie putere a lui 2")
        if self.size % self.line_size != 0:
           raise ValueError("Cache size-ul trebuie sa fie multiplu de line size")
        if (self.size // self.line_size) % self.associativity != 0:
           raise ValueError("Numarul de linii din cache trebuie sa fie multiplu de asociativitate")
        if self.write_policy not in ['write-through', 'write-back']:
           raise ValueError("Politica de scriere trebuie sa fie 'write-through' sau 'write-back'")
        if type(self.size) is not int or type(self.line_size) is not int or type(self.associativity) is not int:
           raise ValueError("Size, line size si associativity trebuie sa fie intregi")
        if self.size <= 0 or self.line_size <= 0 or self.associativity <= 0:
           raise ValueError("Size, line size si associativity trebuie sa fie pozitive")

    def print_stats(self):

        stats = self.get_stats()

        print(f"\n{'=' * 50}")
        print(f"cache stats")
        print(f"{'=' * 50}")
        print(f" config:")
        print(f"size:           {self.size} bytes")
        print(f"line size:      {self.line_size} bytes")
        print(f" associativity: {self.associativity}-way")
        print(f" Sets:          {self.num_sets}")
        print(f" Write policy:  {self.write_policy}")

        print(f" total accesses: {stats['total_accesses']}")
        print(f"  cache-hits:           {stats['hits']} ({stats['hit_rate'] * 100:.1f}%)")
        print(f"  misses:         {stats['misses']} ({stats['miss_rate'] * 100:.1f}%)")
        print(f"  evictions:      {stats['evictions']}")
        print(f" write-backs:    {stats['write_backs']}")
        print(f"  AMAT:           {stats['amat']:.2f} cycles")
        print(f"Whole data block: {stats}")
        print(f"{'=' * 50}")

    def print_contents(self):

        print(f"\nmy cache config:")
        print(f"{'=' * 50}")
        for set_idx, cache_set in enumerate(self.sets):
            print(f"Set {set_idx}:", end=" ")
            for way_idx, line in enumerate(cache_set):
                print(f"Way{way_idx}:{line}", end=" ")
            print()
        print(f"{'=' * 50}")

if __name__ == "__main__":
    try:

        cache = Cache(size=64, line_size=16, associativity=2, write_policy='write-back')

        addresses = [0x00, 0x10, 0x20, 0x00, 0x10, 0x30, 0x10, 0x10,0x10,0x40,0x20]

        for addr in addresses:
            hit, latency = cache.access(addr, is_write=False)
            print(f"for the adress: {addr:#04x}: {'Hit' if hit else 'Miss'}, Latency: {latency} cycles")

        cache.print_stats()
        cache.print_contents()
    except ValueError as ve:
        print(f"Error initializing cache: {ve}")