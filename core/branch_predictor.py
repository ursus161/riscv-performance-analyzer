import math


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

    def _hash(self,pc):
        #vreau sa evit coliziunile in tabelul meu, o coliziune reprezinta ca 2(sau mai multe branchuri) ar avea acc predictie, implicit acuratetea s-ar strica  

        history_val = 0
        for bit in self.history:
            history_val = (history_val << 1) | (1 if bit == 1 else 0)

        index = (pc ^ history_val) % self.table_size
        return index


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
