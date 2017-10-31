# find-political-donors
Insight Data Engineering Fellow Program (http://insightdataengineering.com/)

Alexander Batanov
batanov@gmail.com
m: 212-810-9286

* Introduction

Please note that Python code in this project and corresponding test files had been developed on Windows using IPython notebook.

Specifically GraphLab Create installation from Coursera Machine Learning Specialization had been used. Python version is 2.7.

The Python code itself is contained in a single file find_political_donors.py which had been thoroughly tested. Note that run.sh had not been tested on mac or Linux. Equivalent ran.bat had been tested on Windows using PowerShell. Command lines in run.bat and in run.sh are identical.

All output files had been generated on my Windows laptop (Surface 3). Test_5 input file was downloaded from FEC site. It is the same as itcont_2018_20170908_20171103.txt that can be found in one of the archives on http://classic.fec.gov/finance/disclosure/ftpdet.shtml.  

Test_4 input file was manually modified to create invalid data in order to check validate() function.

Each input directory in the insight_testsuite has a readme.txt file.

I only used libraries that come with Python 2.7 in my program. See import statements at the top of the find_political_donors.py file.


* Approach

After reviewing the problem statement, it became clear that in order solve running median problem, the program has to see all input values. While calculating running counts and amounts can be achieved in chunks, the median calculation cannot be chunked up.

I have use minheap/maxheap algorithm to calculate running median for each valid row in the input file. The algorithm is described in this StackOverflow article:

https://stackoverflow.com/questions/10657503/find-running-median-from-a-stream-of-integers

This algorithm is encapsulated in Contributions class, which supports only one update method add(amount). Contributions instances privately hold minheap and maxheaps as well as running counts and total of all the contributions observed so far for either Recipient/Zip or Recipient/Date unique combinations. I have used Python's built-in heapq library, which implements minheap only. Maxheap is implemented by simply negating elements that are added to it and "un-negating" them on retrieval.

To accumulate/aggregate contributions, I use two dictionaries, rzDict and rdDict, which store a single Contributions instance for each unique Recipient/Zip or Recipient/Date key. Both dictionaries are updates for each valid line in the input file barring invalid respective Zip and Date values. rzDict is used immediately to populate medianvals_by_zip.txt file, while rdDict accumulates data while calculating running median so that we do not need to sort contributions at the end. rdDict keys are sorted using sorted() method (which I believe creates a new instance of the dictionary). Alternative implementation could be to use OrderedDict available in Python 3.

In order to "filter out" invalid data, for each line of input file, global validate(line) function is used. It returns a dictionary with the keys 'recipient', 'zip', 'date', 'amount'. If the entire line needs to be skipped, None is returned instead of dictionary. If input line can be used for either Recipient/Zip or Recipient/Date, or both, a dictionary is returned. If either zip or date values are invalid, they will be replaced with None assigned to respective dictionary entries.

Note that data validation rules are documented in detail inside validate() finction itself.

I did notice that the dates in the input and the sample output file appear in MMDDYYYY format, which does not support chronological ordering. I did not change the format, but noted in my comments that the data can be easily re-formatted by using the following line of code:

date = fields[13][4:]+fields[13][:4]


* Observations

While smaller size input files (~1M) had been processed on my Surface 3 table within a second, larger itcont_2018_20170908_20171103.txt file (~45M) took about an hour to process. Calculation was slow but it did complete. I relied on my computer paging and Python memory management to handle growing space occupied by Contributions class instances.

Alternative probabilistic approaches to running median calculation can be explored further. See algorithm described by by Cameron Purdy here: https://www.quora.com/What-is-the-distributed-algorithm-to-determine-the-median-of-arrays-of-integers-located-on-different-computers.

My understanding is that in Python the following construct had been optimized to be memory efficient:

with open(filename_in, 'r') as file_in:
	for line in file_in: 

It reads one file line at a time into memory and then discards it before reading the next one (as opposed to reading in the entire file). I have explored iterables to achieve the same explicitly, and found performance to be similar.

with open(filename_in, 'r') as file_in:
	for line in iter(f.readline, ''):

  
