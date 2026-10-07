# Your names:
# Kanav Nagpal
# Spire ID: 35296223
# Gabriel Walters
# Spire ID: 35319051


# no other modules allowed
import random, time, sys


class Dictionary:

    def __init__(self, filename=None):
        self.__words = []
        self.__index = -1
        self.__steps = 0
        self.__score_list = []

        if filename is None:
            self.__name = "N/A"
        else:
            try:
                with open(filename, encoding='utf-8') as f:
                    for line in f:
                        self.__words.append(line.strip())

                print("Load " + filename)
                self.__name = filename

            except FileNotFoundError:
                print("File " + filename + " does not exist!")
                sys.exit(0)

        random.seed(8)

    def get_name(self):
        return self.__name

    def get_size(self):
        return len(self.__words)

    def get_random_list(self, n):
        return random.sample(self.__words, n)

    def get_index(self):
        return self.__index

    def insert(self, element):
        self.__words.append(element)

    def display(self, score=False):
        if not score:
            for i in self.__words:
                print(i)
        else:
            for i in range(self.get_size()):
                print(self.__words[i], self.__score_list[i])

    def shuffle(self):
        t1 = time.process_time()

        for i in range(len(self.__words) - 1, 0, -1):
            j = random.randint(0, i)
            self.__words[i], self.__words[j] = (
                self.__words[j],
                self.__words[i]
            )

        t2 = time.process_time()
        return t2 - t1

    def lsearch(self, item):
        status = False

        for i in range(0, len(self.__words)):
            if self.__words[i] == item:
                status = True
                self.__index = i
                break

        return status

    def selection_sort(self):  # provided to you
        """Perfom selection sort, must return the time it takes to sort the list of words
        Remark: Routine works 'in-place'"""

        t1 = time.process_time()  # capture time
        n = self.get_size()

        for out in range(n - 1):  # outer loop
            # find minimum between out+1 and n-1
            imin = out

            for i in range(out + 1, n):  # inner loop
                if self.__words[i] < self.__words[imin]:
                    imin = i  # update minimum index

            # swap (3 step here)
            temp = self.__words[imin]
            self.__words[imin] = self.__words[out]
            self.__words[out] = temp

        t2 = time.process_time()  # capture time
        return t2 - t1

    def bsearch(self, item):
        left = 0
        right = len(self.__words) - 1
        steps = 1  # Minimum number of steps to find item has to be 1

        while left <= right:
            mid = (left + right) // 2

            if self.__words[mid] == item:
                self.__index = mid
                self.__steps = steps
                return True

            elif self.__words[mid] < item:
                left = mid + 1

            else:
                right = mid - 1

            steps += 1

        self.__index = left
        self.__steps = steps
        return False

    @staticmethod  # provided to you
    def get_word_combination(word, combs=['']):
        """return a list that contains all the letter combinations
        (all length) of the input 'word'"""

        if len(word) == 0:
            return combs

        head, tail = word[0], word[1:]
        combs = combs + list(map(lambda x: x + head, combs))

        return Dictionary.get_word_combination(tail, combs)

    @staticmethod
    def sort_word(word):  # to complete
        """must return a string with letters included in 'word'
        that are now sorted"""

        letters = list(word)

        for i in range(len(letters) - 1):
            for j in range(i + 1, len(letters)):
                if letters[i] > letters[j]:
                    temp = letters[i]
                    letters[i] = letters[j]
                    letters[j] = temp

        return ''.join(letters)

    def insertion_sort(self):
        t1 = time.process_time()
        n = self.get_size()

        for i in range(1, n):
            key = self.__words[i]
            j = i - 1

            while j >= 0 and self.__words[j] > key:
                self.__words[j + 1] = self.__words[j]
                j -= 1

            self.__words[j + 1] = key

        t2 = time.process_time()
        return t2 - t1

    def enhanced_insertion_sort(self):
        t1 = time.process_time()
        n = self.get_size()

        for i in range(1, n):
            key = self.__words[i]
            low = 0
            high = i

            while low < high:
                mid = (low + high) // 2

                if self.__words[mid] <= key:
                    low = mid + 1
                else:
                    high = mid

            j = i

            while j > low:
                self.__words[j] = self.__words[j - 1]
                j -= 1

            self.__words[low] = key

        t2 = time.process_time()
        return t2 - t1

    def save(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines([i + "\n" for i in self.__words])

        print("Save", filename)

    def get_steps(self):
        return self.__steps

    
    def spell_check(self, file):
        try:
            f = open(file, "r", encoding="utf-8")
        except FileNotFoundError:
            print('File', file, 'does not exist!')
            return

        print()
        with f:
            punc = r"""'!()-[]{};:'"\,<>./?@#$%^&*_~'""" + "\u2018\u2019\u201c\u201d\u2026"

            for nextline in f:
                if nextline == "\n":
                    print()
                    continue

                nextwords = nextline.rstrip().split(' ')

                for i in range(len(nextwords)):
                    word = nextwords[i]
                    word_low = word.strip(punc).lower()

                    if not self.bsearch(word_low):
                        nextwords[i] = '(' + word + ')'

                print(' '.join(nextwords))

    def anagram(self, word):
        anagrams = []
        sorted_word = Dictionary.sort_word(word)

        for current_word in self.__words:
            if len(current_word) == len(word):
                sorted_current_word = Dictionary.sort_word(current_word)

                if sorted_current_word == sorted_word:
                    anagrams.append(current_word)

        return anagrams

    def compute_score_scrabble(self):
        score_dict = {
            'e': 1, 'a': 1, 'i': 1, 'n': 1, 'r': 1, 't': 1, 'l': 1, 's': 1, 'u': 1,
            'd': 2, 'g': 2,
            'b': 3, 'c': 3, 'm': 3, 'p': 3,
            'f': 4, 'h': 4, 'v': 4, 'w': 4, 'y': 4,
            'k': 5,
            'j': 8, 'x': 8,
            'q': 10, 'z': 10
        }

        self.__score_list = []  # reset so repeated calls do not duplicate scores

        for word in self.__words:
            score = 0

            for ch in word:
                score += score_dict.get(ch.lower(), 0)  # 0 for apostrophes, accents, etc.

            self.__score_list.append(score)

    def score_sort(self):
        t1 = time.process_time()  # capture time
        n = self.get_size()

        for i in range(1, n):
            key_word = self.__words[i]
            key_score = self.__score_list[i]
            j = i - 1

            # strict > keeps the sort stable (ties keep original order)
            while j >= 0 and self.__score_list[j] > key_score:
                self.__words[j + 1] = self.__words[j]
                self.__score_list[j + 1] = self.__score_list[j]
                j -= 1

            self.__words[j + 1] = key_word
            self.__score_list[j + 1] = key_score

        t2 = time.process_time()  # capture time
        return t2 - t1

    def crack_lock(self, lock):
        result = Dictionary()

        if len(lock) == 0 or any(len(options) == 0 for options in lock):
            return result

        c = 1

        for options in lock:
            c *= len(options)

        trials = 6 * c

        for _ in range(trials):
            candidate = ""

            for options in lock:
                candidate += options[random.randint(0, len(options) - 1)]

            if self.bsearch(candidate):
                if not result.lsearch(candidate):
                    result.insert(candidate)

        return result


########################################################################
########################################################################


def main():

    ### step-1 test constructor
    name = input("Enter dictionary name (from file 'name'.txt): ")
    dict1 = Dictionary(name + ".txt")

    ### step-2 test get_name, get_size, get_random_list
    print('Name main dictionary:', dict1.get_name())
    print('Size main dictionary:', dict1.get_size())
    print("Five random words:", end=" ")

    rlist = dict1.get_random_list(5)  # 5 means the number of random words we want

    for w in rlist:
        print(w, end=" ")

    print("\n")

    ### step-3 test constructor again
    dict2 = Dictionary()
    print('Name extracted dictionary:', dict2.get_name())

    ### step-4 test insert and display
    for w in rlist:
        dict2.insert(w)

    print('Display extracted dictionary:')
    dict2.display()

    ### step-5 test shuffle
    t = dict2.shuffle()

    print('\nExtracted dictionary shuffled in %ss:' % t)
    print('Display extracted dictionary:')
    dict2.display()

    ### step-6 test linear search
    word = "morning"

    print(
        "\nLinear search for the word '%s' in extracted dictionary"
        % word
    )

    status = dict2.lsearch(word)

    print(
        "Is '%s' found: %s at index %s"
        % (word, status, dict2.get_index())
    )

    ### step-7 sort extracted using selection sort (provided to you)
    t = dict2.selection_sort()

    print('\nExtracted dictionary sorted in %ss:' % t)
    print('Display extracted dictionary:')
    dict2.display()

    ### step-8 test binary search (find it)
    words = ["morning", "night"]

    for word in words:
        print(
            "\nBinary search for the word '%s' in extracted dictionary"
            % word
        )

        status = dict2.bsearch(word)  # binary search

        if (status):  # found it!!
            print(
                "Is '%s' found: %s at index %s"
                % (word, status, dict2.get_index())
            )

        else:  # Nope did not find it
            print(
                "'%s' is not found so it must be inserted at index %s"
                % (word, dict2.get_index())
            )


## call the main function if this file is directly executed
if __name__ == "__main__":
    main()