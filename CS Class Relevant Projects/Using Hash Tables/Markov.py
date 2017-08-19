# CS122 W'17: Markov models and hash tables
# Steven Wei

'''
Tested using:

for ((i=1;i<=50;i++)); do 
python3 Markov.py speeches/obama1+2.txt speeches/mccain1+2.txt 
speeches/obama-mccain3/MCCAIN-$i.txt 3; 
done

& 

for ((i=1;i<=50;i++)); do 
python3 Markov.py speeches/obama1+2.txt speeches/mccain1+2.txt 
speeches/obama-mccain3/OBAMA-$i.txt 3; 
done

'''
import sys
import math
import Hash_Table

HASH_CELLS = 57

class Markov:

    def __init__(self,k,s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.table1 = Hash_Table.Hash_Table(HASH_CELLS, 0)
        self.table2 = Hash_Table.Hash_Table(HASH_CELLS, 0)
        self.k = k
        self.s = s
        self.add_kcounts()

    def add_kcounts(self):
        '''
        This function is used in the constructor to create the model statistics
        by finding the frequency of each k-gram and k-char-gram.
        '''
        total = len(self.s)

        for i, char in enumerate(self.s):
            start_num = ((i-self.k) % total)
            end_num = ((i-1) % total)

            if end_num < start_num:
                t1 = self.s[start_num:total]
                t2 = self.s[0:end_num+1]
                kgram = t1 + t2
            if end_num >= start_num:
                kgram = self.s[start_num:end_num+1]

            kchargram = kgram + char
            original_count = self.table1.lookup(kgram)
            self.table1.update(kgram, 1 + original_count)
            original_count = self.table2.lookup(kchargram)
            self.table2.update(kchargram, 1 + original_count)

    def log_probability(self,s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''
        total_probability = 0
        total = len(s)

        for i, char in enumerate(s):
            start_num = ((i-self.k) % total)
            end_num = ((i-1) % total)

            if end_num < start_num:
                t1 = s[start_num:total]
                t2 = s[0:end_num+1]
                kgram = t1 + t2

            if end_num >= start_num:
                kgram = s[start_num:end_num+1]

            kchargram = kgram + char
            M = self.table2.lookup(kchargram)
            N = self.table1.lookup(kgram)
            S = len(set(s))
            probability = math.log((1 + M) / (N + S))
            total_probability += probability

        return total_probability

def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    s1 = Markov(order, speech1)
    s2 = Markov(order, speech2)

    str_len = len(speech3)

    likelihood1 = s1.log_probability(speech3) / str_len
    likelihood2 = s2.log_probability(speech3) / str_len

    if likelihood1 > likelihood2:
        conclusion = 'A'

    if likelihood2 > likelihood1:
        conclusion = 'B'

    if likelihood2 == likelihood1:
        conclusion = 'A and B'

    return (likelihood1, likelihood2, conclusion)  

def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


if __name__=="__main__":
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)
    
    with open(sys.argv[1], "rU") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "rU") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "rU") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)

