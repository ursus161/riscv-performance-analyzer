import math


def _scramble_pc(pc):
    return pc ^ (pc >> 3) ^ (pc >> 6) ^ (pc >> 9)


class BTB:
    def __init__(self, size=64):
        self.size = size
        self.entries = [None] * size  # fiecare entry: {'tag': pc, 'target': addr}
        self.hits = 0
        self.misses = 0

    def _index(self, pc):
        return _scramble_pc(pc) % self.size

    def lookup(self, pc):
        entry = self.entries[self._index(pc)]
        if entry and entry['tag'] == pc:
            self.hits += 1
            return entry['target']
        self.misses += 1
        return None

    def update(self, pc, target):
        self.entries[self._index(pc)] = {'tag': pc, 'target': target}

    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            'total_lookups': total,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 4),
        }

    def print_stats(self):
        stats = self.get_stats()
        print(f"\n{'=' * 50}")
        print(f"Branch Target Buffer (BTB)")
        print(f"{'=' * 50}")
        print(f"  Size:          {self.size} entries")
        print(f"  Total lookups: {stats['total_lookups']}")
        print(f"  Hits:          {stats['hits']} ({stats['hit_rate'] * 100:.1f}%)")
        print(f"  Misses:        {stats['misses']}")
        print(f"{'=' * 50}")


class PerceptronPredictor:
    def __init__(self, table_size=64, history_length=8):
        self.table_size = table_size
        self.history_length = history_length
        # Jimenez & Lin threshold: antreneaza dacă |y| <= 0 sau predictie gresita
        # ideea acestui threshold e evitarea unui overfit
        self.threshold = int(1.93 * history_length + 14)

        # weights[i] = [bias, w1..w_h], unul per intrare în tabel
        self.weights = [[0] * (history_length + 1) for _ in range(table_size)]
        # global history: +1 = taken, -1 = not-taken
        self.history = [-1] * history_length

        self.total = 0
        self.correct = 0

    def _sigmoid(self, x):
        return 1.0 / (1.0 + math.exp(-x))

    def _hash(self, pc):
        history_val = 0
        for bit in self.history:
            history_val = (history_val << 1) | (1 if bit == 1 else 0)

        return (_scramble_pc(pc) ^ history_val) % self.table_size


    def _output(self, pc):

        w = self.weights[self._hash(pc)] 
        return w[0] + sum(w[i + 1] * self.history[i] for i in range(self.history_length))
    #acel w[0] e bias ul meu, fara el un branch always taken ar fi 

    def predict(self, pc):
        y = self._output(pc)
        confidence = self._sigmoid(y)   
        return confidence > 0.5, confidence

    def update(self, pc, actually_taken):
        t = 1 if actually_taken else -1
        y = self._output(pc)
        predicted = y > 0

        self.total += 1
        if predicted == actually_taken:
            self.correct += 1

        # train daca e predictie gresita sau confidence mic in rezultat
        if predicted != actually_taken or abs(y) <= self.threshold:
            w = self.weights[self._hash(pc)]
            w[0] += t
            for i in range(self.history_length):
                w[i + 1] += t * self.history[i]

        self.history = [t] + self.history[:-1]

    def get_stats(self):
        accuracy = self.correct / self.total if self.total > 0 else 0
        return {
            'total_branches': self.total,
            'correct': self.correct,
            'mispredictions': self.total - self.correct,
            'accuracy': round(accuracy, 4),
        }

    def print_stats(self):
        stats = self.get_stats()
        print(f"\n{'=' * 50}")
        print(f"Branch Predictor (Perceptron)")
        print(f"{'=' * 50}")
        print(f"  History length:  {self.history_length}")
        print(f"  Table size:      {self.table_size} entries ")
        print(f"  Threshold (θ):   {self.threshold}")
        print(f"  Total branches:  {stats['total_branches']}")
        print(f"  Corecte:         {stats['correct']} ({  stats['accuracy'] * 100:.1f}%)")
        print(f"  Mispredictions:  {stats['mispredictions' ]}")
        print(f"{'=' * 50}")
