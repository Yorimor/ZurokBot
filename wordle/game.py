from wordle import words
from wordle.exceptions import GuessTooShort, GuessNotInWords, GuessAlreadyUsed, GuessLimitReached


class WordleGame:
    def __init__(self):
        self.game, self.target = words.todays_wordle()

        self.guess_count = 0
        self.guessed_words = []
        self.wordle_lines = []
        self.guesses_max = 6

        self.yes_tile = "🟩"
        self.maybe_tile = "🟨"
        self.no_tile = "⬛"

    def new_game(self, rand: bool = False):
        self.game, self.target = words.todays_wordle(rand=rand)
        self.guess_count = 0
        self.guessed_words = []
        self.wordle_lines = []

    def guess_wordle(self, guess: str):
        if len(guess) != 5:
            raise GuessTooShort

        if self.guess_count == self.guesses_max:
            raise GuessLimitReached

        if guess in self.guessed_words:
            raise GuessAlreadyUsed

        if guess not in words.targets and guess not in words.others:
            raise GuessNotInWords

        self.guess_count += 1
        self.guessed_words.append(guess)

        _target = self.target[:]
        _guess = guess[:]

        done = {}

        wordle_guess = ["" for x in range(5)]
        for i, (g_letter, t_letter) in enumerate(zip(_guess, _target)):
            if g_letter == t_letter:
                wordle_guess[i] = self.yes_tile
                _target = _target[:i] + "-" + _target[i+1:]
                _guess = _guess[:i] + "-" + _guess[i+1:]

                done[g_letter] = done.get(g_letter, 0) + 1

        for i, (g_letter, t_letter) in enumerate(zip(_guess, _target)):
            if g_letter == "-":
                continue

            if g_letter in _target and done.get(g_letter, 0) < self.target.count(g_letter):
                wordle_guess[i] = self.maybe_tile
                done[g_letter] = done.get(g_letter, 0) + 1
            else:
                wordle_guess[i] = self.no_tile

        wordle_guess = "".join(wordle_guess)
        self.wordle_lines.append(wordle_guess)
        return wordle_guess

    def share_game(self):
        score = self.guess_count

        if not all(c == self.yes_tile for c in self.wordle_lines[-1]):
            score = "X"

        title = f"Wordle {self.game} {score}/6"

        wordle_str = [title, ""] + self.wordle_lines

        return score, "\n".join(wordle_str)


if __name__ == "__main__":
    w = WordleGame()

    w.target = "grass"

    gs = ["apsis", "sasin", "sassy", "snide", "watch", "shade"]
    for x in gs:
        g = w.guess_wordle(x)
        print(x, g)

    print(w.share_game())
