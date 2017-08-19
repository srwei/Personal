#Steven Wei
from mrjob.job import MRJob

class MRVisitedBothYears(MRJob):
    '''
    MRJob class that outputs people that were visitors at the White House
    in both 2009 and 2010.
    '''
    def mapper(self, _, visits):
        '''
        Takes the csv file (per line) and yields the name of the person as the key
        and which year they visited as the value
        '''
        visits = visits.strip()
        visits = visits.split(",")
        lastname = visits[0]
        firstname = visits[1]
        middlename = visits[2]
        date = visits[-1]
        if date is not '':
            if date != 'RELEASE_DATE':
                year = date.split("/")[2]
                if year is not '':
                    if middlename == '':
                        name = firstname + ' ' + lastname
                    else:
                        name = firstname + ' ' + middlename + ' ' + lastname
                    yield name, year
    
    def combiner(self, name, year):
        '''
        Takes the name, years output from the mapper and only yields 
        the unique values
        '''
        for uniqueyear in set(year):
            yield name, uniqueyear

    def reducer(self, name, year):
        '''
        Takes the name, years output and compiles them under the same
        name and yields the names that visited both years
        '''
        if len(set(year)) == 2:
            yield name, None

if __name__ == '__main__':
    MRVisitedBothYears.run()