#Steven Wei
from mrjob.job import MRJob

class MRMostFreqVisitors(MRJob):
    '''
    MRJob class that outputs the people that were visitors at the White House at
    least 10 times during 2009 and 2010
    '''
    def mapper(self, _, visits):
        '''
        Takes the csv file (per line) and yields the name of the person as the key
        and the value of 1 
        '''
        visits = visits.strip()
        visits = visits.split(",")
        lastname = visits[0]
        firstname = visits[1]
        middlename = visits[2]
        if middlename == '':
            name = firstname + ' ' + lastname
        else:
            name = firstname + ' ' + middlename + ' ' + lastname
        yield name, 1

    def reducer(self, name, counts):
        '''
        Takes the name, value output and yields the names of 
        visitors that visited at least 10 times by summing counts
        '''
        if sum(counts) > 9:
            yield None, name

    def combiner(self, name, counts):
        '''
        Takes the name, value output from mapper and yields the the name and
        the sum of the received counts from the respective mapper
        '''
        yield name, sum(counts)

if __name__ == '__main__':
    MRMostFreqVisitors.run()