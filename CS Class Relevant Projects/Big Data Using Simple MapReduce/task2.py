#Steven Wei
from mrjob.job import MRJob
from mrjob.step import MRStep
import heapq

class MRMostVisited(MRJob):
    '''
    MRJob class that outputs the top 10 most frequent visitors at the
    White House in 2009 and 2010
    '''

    def mapper_visits(self, _, visits):
        '''
        Takes the csv file (per line) and yields the name of the person visited as 
        the key and the value of 1 
        '''
        visits = visits.strip()
        visits = visits.split(",")
        lastname = visits[19]
        firstname = visits[20]

        if lastname is not '' :
            if firstname != 'VISITORS' and lastname != 'OFFICE':
                name = firstname + ' ' + lastname
                yield name, 1

    def combiner_visits(self, name, counts):
        '''
        Takes the name, counts from the mapper and sums them together
        '''
        yield name, sum(counts)

    def reducer_init(self):
        '''
        Initializes the heap that will be used to hold the top 10 visitors 
        '''
        self.heap_list = []

    def reducer_visit_counter(self, name, counts):
        '''
        Takes the name, counts from mapper or combiner and sums them together
        '''
        yield name, sum(counts)

    def reducer2(self, name, counts):
        '''
        Takes the name, and total counts of each visitor and inserts them into
        the initialized heap
        '''
        heapq.heappush(self.heap_list,(sum(counts), name))

    def reducer_final(self):
        '''
        Takes the top 10 visitors from the heap and returns their name
        '''
        top_10 = heapq.nlargest(10, self.heap_list)
        for (counts, name) in top_10:
            yield name, None

    def steps(self):
        '''
        Sets the steps of the MRJob function in order to run. First step is to generate
        the name, total visits pair. Second step is to generate the top 10 visitors 
        using a heap.
        '''
        return [

            MRStep(
            mapper = self.mapper_visits, 
            combiner = self.combiner_visits, 
            reducer = self.reducer_visit_counter
            ),
            MRStep(
                reducer_init = self.reducer_init, 
                reducer = self.reducer2,
                reducer_final = self.reducer_final,
            )
        ]

if __name__ == '__main__':
    MRMostVisited.run()