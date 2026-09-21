# Your names:
#
#
#
#

# no other modules allowed
import random,time,sys




class Dictionary:



    #### To complete



    
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
        pass # to remove





    

    
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
