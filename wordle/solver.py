from wordle.game import WordleGame
from wordle.words import targets, others
import random
from enum import Enum
import os
from copy import deepcopy


class Mode(Enum):
    EXACT_COUNT = 0
    MIN_COUNT = 1
    POS_EXACT = 2
    POS_MIN = 3


class WordleSolver:
    def __init__(self):
        random.seed(os.urandom(54))
        self.game = WordleGame()

        self.words = targets.copy() + others.copy()

        self.guessed_words = []

        self.yes_tile = "🟩"
        self.maybe_tile = "🟨"
        self.no_tile = "⬛"

        self.tile_values = {self.yes_tile: 1, self.maybe_tile: 0, self.no_tile: -1}

        self.known = {i: "" for i in range(5)}

        self.count_zero = []
        self.count_some = {}
        self.count_exact = {}

    def setup(self, rand: bool = False):
        self.count_zero = []
        self.count_some = {}
        self.count_exact = {}
        self.known = {i: "" for i in range(5)}

        self.game.new_game(rand)
        self.guessed_words = []
        self.words = targets.copy() + others.copy()

    def play(self, rand: bool = False):
        self.setup(rand)

        count = 0
        loop_count = 0
        while count < 6:
            guess, result = self.make_guess()
            # print(guess, result)

            if all(c == self.yes_tile for c in result):
                break

            self.filter_words(guess, result)
            count += 1

            if len(self.words) == 0:
                self.setup()
                count = 0
                loop_count += 1
                if loop_count < 10:
                    return None

        return self.game.share_game()

    def make_guess(self):
        guess = random.choice(self.words)
        self.guessed_words.append(guess)
        result = self.game.guess_wordle(guess)
        # print(guess, result)
        return guess, result

    def filter_words(self, guess, result):
        letters = {}
        for i, (letter, tile) in enumerate(zip(guess, result)):
            if letter not in letters:
                letters[letter] = {self.yes_tile: 0, self.no_tile: 0, self.maybe_tile: 0}

            letters[letter][tile] += 1

            if tile == self.yes_tile:
                self.known[i] = letter

        for letter, data in letters.items():

            count = data[self.maybe_tile] + data[self.yes_tile]

            if data[self.no_tile] > 0:
                if count == 0:
                    self.count_zero.append(letter)
                elif letter not in self.count_exact:
                    self.count_exact[letter] = count
                elif self.count_exact[letter] < count:
                    self.count_exact[letter] = count

            else:
                if letter not in self.count_some:
                    self.count_some[letter] = count
                elif self.count_some[letter] < count:
                    self.count_some[letter] = count

        self.count_zero = list(set(self.count_zero))
        for l in self.count_exact:
            if l in self.count_some:
                del self.count_some[l]

        _words = [w for w in self.words if self.is_valid_word(w)]

        if self.game.target not in _words:
            print(f"{self.known=}")
            print(f"{self.count_zero=}")
            print(f"{self.count_some=}")
            print(f"{self.count_exact=}")
            print(f"{len(_words)=} {self.game.target=}")
            print(f"{_words[:20]=}")
            print(f"{self.guessed_words}")
            # exit()

        self.words = _words

    def is_valid_word(self, word):
        if word in self.guessed_words:
            return False

        for letter in self.count_zero:
            if letter in word:
                return False

        for letter, count in self.count_some.items():
            if word.count(letter) < count:
                return False

        for letter, count in self.count_exact.items():
            if word.count(letter) != count:
                return False

        for i, letter in self.known.items():
            if word[i] != letter and letter != "":
                return False

        return True


if __name__ == "__main__":
    random.seed(os.urandom(54))

    scores = []

    amount = 30_000
    for g in range(amount):
        solver = WordleSolver()
        if g % (amount * 0.01) == 0:
            print(g)
        r = solver.play(rand=True)
        scores.append(r[0])

    from collections import Counter
    scores_count = Counter(scores)
    print(scores_count)
