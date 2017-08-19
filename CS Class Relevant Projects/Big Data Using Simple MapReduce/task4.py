#Steven Wei
from mrjob.job import MRJob

class MRBothVisitorVisited(MRJob):
    '''
    MRJob class that outputs people that were visitors and visited at the White House
    in 2009 and 2010. 
    '''

    def mapper(self, _, visits):
        '''
        Takes the csv file (per line) and yields the name of the person as the key
        and whether they were a visitor or visited 
        '''
        visits = visits.strip()
        visits = visits.split(",")
        visitorlastname = visits[0]
        visitorfirstname = visits[1]
        visitedlastname = visits[19]
        visitedfirstname = visits[20]
        date = visits[-1]
        if date is not '':
            if date != 'RELEASE_DATE':
                year = date.split("/")[2]
                if year is not '':
                    name = visitorfirstname + ' ' + visitorlastname
                    yield name, 'visitor'

                    if visitedlastname is not '' :
                        if visitedfirstname != 'VISITORS' and visitedlastname != 'OFFICE':
                            name = visitedfirstname + ' ' + visitedlastname
                            yield name, 'visited'
    
    def combiner(self, name, visits):
        '''
        Takes the name, visitor/visited output from the mapper and only yields 
        the unique values
        '''
        for uniquevalues in set(visits):
            yield name, uniquevalues
    
    def reducer(self, name, visits):
        '''
        Takes the name, visitor/visited output and compiles them under the same
        name and yields the names that were both visited and visitors
        '''
        if len(set(visits)) == 2:
            yield name, None

if __name__ == '__main__':
    MRBothVisitorVisited.run()