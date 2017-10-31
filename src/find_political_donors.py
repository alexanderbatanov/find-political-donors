# this code is written for Python 2.7

import sys
import heapq
import re
from types import *
from find_political_donors import *

def main(argv):

    filename_in=''
    filename_out1=''
    filename_out2=''
   
    filename_in=sys.argv[1]
    filename_out1=sys.argv[2]
    filename_out2=sys.argv[3]

    rzDict = {} # dictionary to store Contributions object for each unique recipient/zip combination
    rdDict = {} # dictionary to store Contributions object for each unique recipient/date combination
    
    try:

        with open(filename_in, 'r') as file_in:

            with open(filename_out1, 'w') as file_out1:

                for line in file_in:

                    # validate() returns None if the line has to be complely skipped (e.g. invalid recipient or amount, etc.)
                    # otherwise it will return a disctionary with keys: 'recipient', 'zip', 'date', 'amount'
                    # if zip or date are invalid, None value will be returned in the corresponding dictionary key
                    fields = validate(line)

                    if fields:

                        recipient = fields['recipient']
                        zip = fields['zip']
                        date = fields['date']
                        amount = fields['amount']

                        if zip:

                            # add fields to the recipient/zip dictionary
                            key = recipient+'|'+zip
                            if key not in rzDict.keys():
                                c = Contributions()
                                c.add(amount)
                                rzDict[key] = c
                            else:
                                rzDict[key].add(amount)

                            # write to the first output file
                            file_out1.write(key+'|'+str(rzDict[key].median())+'|'+str(rzDict[key].count())+'|'+str(rzDict[key].total())+'\n')

                        if date:

                            # add fields to recipient/date dictionary
                            key = recipient+'|'+date
                            if key not in rdDict.keys():
                                c = Contributions()
                                c.add(amount)
                                rdDict[key] = c
                            else:
                                rdDict[key].add(amount)

            # sort the recipient/date dictionary and write it to the second output file
            with open(filename_out2, 'w') as file_out2:

                for key in sorted(rdDict):

                    file_out2.write(key+'|'+str(rdDict[key].median())+'|'+str(rdDict[key].count())+'|'+str(rdDict[key].total())+'\n')

    except IOError as e:

        print e

if __name__ == "__main__":
    main(sys.argv[1:])


def validate(line):

    # validate relevant input fields and return them in a dictionary
    # if entire row is invalid, return None
    # if only zip or date fields are invalid, assign None respectively and return dictionary
    # output dictionary structure (keys: 'recipient', 'zip', 'date', 'amount')
    fields = {}
   
    # check if the line is empty
    # if empty, return None (so that the line is skipped by caller)    
    if line == '\n':
        return None
    
    try:
 
        line_fields = line.split('|')

        # check expected number of fields
        # if not what expected, return None (so that the line is skipped by caller)
        if len(line_fields) <> 21:
            return None

        # check if OTHER_ID field is populated
        # if populated, return None (so that the line is skipped by caller)
        if line_fields[15] <> '':
            return None

        # check CMTE_ID field: error if blank
        # if no errors, assign to output dictionary and continue processing
        # if errors, return None (so that the line is skipped by caller)
        # assumption: blank charachters are allowed; leading and trailing blank characters are not truncated
        if line_fields[0] == '':
            return None
        else:
            fields['recipient'] = line_fields[0]
  
        # check ZIP_CODE field: error if blank, has non-number characters, not 5 or 9 charachters long
        # if no errors, assign first 5 characters to output dictionary and continue processing
        # if errors, assign None to output dictionary and continue processing (the line should be processed by caller)
        # assumption: expected 9 character format is 200033228, not 20003-3228 (in this case use regex '^[0-9]{5}(?:-[0-9]{4})?$')
        # assumption: leading and trailing blank characters are not truncated
        if line_fields[10] == '':
            fields['zip'] = None
        elif not re.match('^[0-9]{5}(?:[0-9]{4})?$', line_fields[10]):
            fields['zip'] = None
        else:
            fields['zip'] = line_fields[10][:5]
   
        # check TRANSACTION_DT field: error if blank, has non-number characters, not 8 charachters long
        # if no errors, assign to output dictionary and continue processing
        # if errors, assign None to output dictionary and continue processing (the line should be processed by caller)
        # assumption: expected format is MMDDYYYY, not YYYYMMDD (in this case uncomment the line below and comment out the one above it)
        # assumption: leading and trailing blank characters are not truncated
        if line_fields[13] == '':
            fields['date'] = None
        elif not re.match('^[0-9]{8}$', line_fields[13]):
            fields['date'] = None
        else:
            fields['date'] = line_fields[13]
            # fields['date'] = line_fields[13][4:]+line_fields[13][:4]

        # check TRANSACTION_AMT field: error if blank, does not represent a signed integer (-12, +12, 12), does not cast to an integer
        # if no errors, cast to integer and assign to output dictionary
        # if errors, return None (so that the line is skipped by caller)
        # assumption: expected format is MMDDYYYY, not YYYYMMDD (in this case uncomment the line below and comment out the one above it)
        # assumption: leading and trailing blank characters are not truncated
        if line_fields[14] == '':
            return None
        elif not re.match('^(\+|-)?\d+$', line_fields[14]):
            return None
        else:
            fields['amount'] = int(line_fields[14])
            
        return fields
            
    except:
      
        # suppress all exceptions
        return None

    
class Contributions(object):
    
    # purpose:
    # tracks running count, total and calculates running median
    # takes contribution amount as integer; rounds median values and returns as integer
    # uses minheap/maxheap algorithm to calculate running median (class hides implementation)
    # requires import heapq 
    # makes attributes private (by convention):

    # methods:
    # add(amount) returns None
    # count() returns integer count of Contributions
    # total() returns integer total of Contributions
    # median() returns integer median of Contributions or None if no Contributions have been added yet
    
    def __init__(self):
        self.__count = 0
        self.__total = 0
        self.__median = None        
        self.__minheap = []
        self.__maxheap = []
        heapq.heapify(self.__minheap)
        heapq.heapify(self.__maxheap)
        self.__amount1 = 0
        self.__amount2 = 0
    
    def __str__(self):
        # return '[Contributions: count '+str(self.__count)+', total '+str(self.__total)+', median '+str(self.__median)+']'
        # debug
        return '[Contributions: count '+str(self.__count)+', total '+str(self.__total)+', median '+str(self.__median)+']'+str(self.__minheap)+str(self.__maxheap)

    def count(self):
        return self.__count
    
    def total(self):
        return self.__total
    
    def median(self):
        return self.__median
    
    def add(self, amount):
        
        # assert that amount is integer
        assert type(amount) is IntType, 'Only integer amounts can be added to Contributions: %r' % amount
        
        self.__count += 1
        self.__total += amount
        
        # calculate running median
        if self.__count == 1:
            
            self.__amount1 = amount
            self.__median = amount
            
        elif self.__count == 2:
            
            self.__amount2 = amount
            self.__median = int(round((self.__amount1 + self.__amount2) / 2.0))
            
            # initialize heaps (negate numbers to implement maxheap)
            if self.__amount1 < self.__amount2:
                heapq.heappush(self.__maxheap, -1 * self.__amount1)
                heapq.heappush(self.__minheap, self.__amount2)
            else:
                heapq.heappush(self.__maxheap, -1 * self.__amount2)
                heapq.heappush(self.__minheap, self.__amount1)

        else:

            # insert amount into one of the heaps
            if amount < -1 * self.__maxheap[0]:
                heapq.heappush(self.__maxheap, -1 * amount)
            else:
                heapq.heappush(self.__minheap, amount)

            # balance the heaps, if necessary
            if len(self.__maxheap) - len(self.__minheap) > 1:
                heapq.heappush(self.__minheap, -1 * heapq.heappop(self.__maxheap))
            elif len(self.__minheap) - len(self.__maxheap) > 1:
                heapq.heappush(self.__maxheap, -1 * heapq.heappop(self.__minheap))
            else:
                pass

            # calculate running median
            if len(self.__maxheap) > len(self.__minheap):
                self.__median = -1 * self.__maxheap[0]
            elif len(self.__minheap) > len(self.__maxheap):
                self.__median = self.__minheap[0]
            else:
                self.__median = int(round((-1 * self.__maxheap[0] + self.__minheap[0]) / 2.0))
