# Your names:
# Kanav Nagpal
# Spire ID: 35296223
# Gabriel Walters
# Spire ID: 35319051

# no other modules allowed
import random,time,sys




class Dictionary:


    def __init__(self, filename=None):
        self.__words = []
        self.__index = -1
        if filename is None:
            self.__name = "N/A"
        else:
            try:
                with open(filename) as f:
                    for line in f:
                        self.__words.append(line.strip())
                print("Load " + filename)
                self.__name = filename[:-4] if filename.endswith(".txt") else filename
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

    def display(self):
        for i in self.__words:
            print(i)

    def shuffle(self):
        t1 = time.process_time()
        for i in range(len(self.__words) -1, 0, -1):
            j = random.randint(0,i)
            self.__words[i], self.__words[j] = self.__words[j], self.__words[i]
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

    def selection_sort(self):    #provided to you
        """Perfom selection sort, must return the time it takes to sort the list of words
        Remark: Routine works 'in-place'"""
        t1 = time.process_time() #capture time
        n=self.get_size()
        for out in range(n-1):        #outer loop
            #find minimum between out+1 and n-1
            imin=out
            for i in range(out+1,n):  #inner loop
                if self.__words[i]<self.__words[imin]: 
                    imin=i #update  minimum index
            #swap (3 step here)
            temp=self.__words[imin]
            self.__words[imin]=self.__words[out]
            self.__words[out]=temp
        t2 = time.process_time() #capture time
        return t2-t1
        
    def bsearch(self, item):
        left = 0
        right = len(self.__words) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.__words[mid] == item:
                self.__index = mid
                return True
            elif self.__words[mid] < item:
                left = mid + 1
            else:
                right = mid - 1
        self.__index=left
        return False
    
    @staticmethod  # provided to you
    def get_word_combination(word, combs=['']):
        """ return a list that contains all the letter combinations (all length) of the input 'word' """
        if len(word) == 0:
            return combs
        head, tail = word[0], word[1:]
        combs = combs + list(map(lambda x: x+head, combs))
        return Dictionary.get_word_combination(tail, combs)

    

    @staticmethod
    def sort_word(word):  # to complete
        """ must return a string with letters included in 'word' that are now sorted"""


        letters = list(word)

        for i in range(len(letters)-1):
            for j in range(i+1,len(letters)):
                if letters[i] > letters[j]:
                    temp = letters[i]
                    letters[i] = letters[j]
                    letters[j] = temp
        return ''.join(letters)






    

    
########################################################################
########################################################################


def main():

    ### step-1 test constructor
    name=input("Enter dictionary name (from file 'name'.txt): ")    
    dict1=Dictionary(name+".txt")

    ### step-2 test get_name, get_size, get_random_list        
    print('Name main dictionary:',dict1.get_name())   
    print('Size main dictionary:',dict1.get_size()) 
    print("Five random words:",end=" ")
    rlist=dict1.get_random_list(5) # 5 means the number of random words we want
    for w in rlist: print(w,end=" ")
    print("\n")

    ### step-3 test constructor again
    dict2=Dictionary()
    print('Name extracted dictionary:',dict2.get_name())
    
    ### step-4 test insert and display
    for w in rlist: dict2.insert(w)
    print('Display extracted dictionary:')
    dict2.display()

    ### step-5 test shuffle 
    t=dict2.shuffle()
    print('\nExtracted dictionary shuffled in %ss:'%t)
    print('Display extracted dictionary:')
    dict2.display()

    ### step-6 test linear search
    word="morning"
    print("\nLinear search for the word '%s' in extracted dictionary"%word)
    status=dict2.lsearch(word)
    print("Is '%s' found: %s at index %s"%(word,status,dict2.get_index()))

    ### step-7 sort extracted using selection sort (provided to you)
    t=dict2.selection_sort()
    print('\nExtracted dictionary sorted in %ss:'%t)
    print('Display extracted dictionary:')
    dict2.display()

    ### step-8 test binary search (find it)
    words=["morning","night"]
    for word in words:
        print("\nBinary search for the word '%s' in extracted dictionary"%word)
        status=dict2.bsearch(word) # binary search
        if (status):  # found it!!
            print("Is '%s' found: %s at index %s"%(word,status,dict2.get_index()))
        else:          # Nope did not find it
            print("'%s' is not found so it must be inserted at index %s"%(word,dict2.get_index()))
    


## call the main function if this file is directly executed
if __name__=="__main__":
    main()
