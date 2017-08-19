# CS122 W'17: Markov models and hash tables
# Steven Wei


TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:

    def __init__(self,cells,defval):
        '''
        Construct a bnew hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted
        '''
        self.table = [(None, None)]* cells
        self.cells = cells
        self.defval = defval
        self.count = 0

    def lookup(self,key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.
        '''
        spot = self.hashval(key)

        while self.table[spot] != (None, None):
            if self.table[spot][0] == key:
                return self.table[spot][1]
            
            else:
                spot = spot + 1
                if spot == self.cells:
                    spot = 0

        return self.defval

    def update(self,key,val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val".
        '''
        if self.count / self.cells >= TOO_FULL:
            self.resize()

        if self.lookup(key) == self.defval:
            spot = self.find_spot(key)
            self.table[spot] = (key, val)
            self.count += 1

        else:
            spot = self.hashval(key)

            while self.table[spot] != (None, None):
                if self.table[spot][0] == key:
                    self.table[spot] = (key, val)
                    break

                else: 
                    spot = spot + 1
                    if spot == self.cells:
                        spot = 0

    def resize(self):
        '''
        Creates a new table by expanding it by the Growth Ratio and then rehashes
        all the previous keys and values into their new indexes
        '''
        old_table = self.table[:]
        self.cells = self.cells * GROWTH_RATIO
        self.table = [(None, None)] * self.cells

        for i, item in enumerate(old_table):
            if item != (None, None):
                spot = self.find_spot(item[0])
                self.table[spot] = item

    def find_spot(self, key):
        '''
        This function takes a key and uses its hash value to find the next available 
        spot using linear probing. It returns the index of that next available spot.
        '''
        spot = self.hashval(key)

        while self.table[spot][0] is not None and self.table[spot][0] != key:
            spot = (spot + 1) % self.cells

        return spot

    def hashval(self, key):
        '''
        This takes a key ands finds the hash value of the key for the particular
        hash table.
        '''
        hashval = hash(key) % self.cells
        return hashval

    def __len__(self):
        return self.count