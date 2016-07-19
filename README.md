##Table of Contents

1. [Challenge Summary] (README.md#challenge summary)

2. [Input and Output] (README.md#input-and-output)

3. [Data Structure] (README.md#data-structure)

4. [Solution] (README.md#solution)

5. [Analysis] (README.md#analysis)

6. [System and Required Packages] (README.md#system-and-required-packages)

7. [Repo directory structure] (README.md#repo-directory-structure)

8. [Future Work] (README.md#future-work)

##Challenge Summary

[Back to Table of Contents] (README.md#table-of-contents)

This challenge requires you to:

- Use Venmo payments that stream in to build a graph of users and their relationship with one another.

- Calculate the median degree of a vertex in a graph and update this each time a new Venmo payment appears. You will be calculating the median degree across a 60-second sliding window.

The vertices on the graph represent Venmo users and whenever one user pays another user, an edge is formed between the two users.


##Input and Output

[Back to Table of Contents] (README.md#table-of-contents)

Input: a text file containing bunch of transaction datas (with regulated format). 

Output: a text file named 'output.txt' in the 'venmo_output' directory.

##Data Structure

[Back to Table of Contents] (README.md#table-of-contents)

If following correct format, each transaction will be read as follows:

<b>[seconds, person_of_interest_a, person_of_interest_b]</b>

    seconds: With any reference time (e.g. time of first transaction), the 'created_time' can be converted into "seconds to reference time".

    person_of_interest: The order of "actor" and "target" is irrevalant in this challenge. (Transaction from a to b and from b to a is the same.) So we sort them here to avoid "a-b" <-> "b-a" problem.

class Node() is used to store:

	1. the name of node
	
	2. the neighbors(edges) of this node, and the corresponding expiring time of each neighbor (edge).
	
	3. the number of connected edge of this node

Two lists are used:

	1. graph - to store nodes (and edges) that are not expired.
	
	2. window - to store "non-repetitive" transactions that are not expired yet.

##Solution

[Back to Table of Contents] (README.md#table-of-contents)

It's actually quite straight forward:

For each newly arrived transaction, steps in flow chart are illustrated as follows:

	1. Check the transaction time and repetitivity to classify into four (green) status as follows. Note that for b. and c., no need to build new edge. But it's required to update expiring time in current edge.
	
	2. According to its status, following actions may be necessary.
	    a. update the window:
	        (1) kick expired transaction out of window, and 
	        (2) cut expired edges in the graph: it took place right after window is updated.
	    b. find new median: only if the graph has changed.
	
	    In some situation these actions are not needed.
	
	3. Output the median.

Flow chart is shown as follows:

![flow-chart] (images/flowchart.png)

	Grey: unknown status
	
	Green: status for sure (new edges are added now if needed).
	
	Blue: actions that take place only when necessary
	
	Orange: output the median

Detailed status (green) explanation:
![status] (images/status.png)

    expired: this transaction can be ignored.
    
    repetitive but useless: this transaction is repetitive, but it's older than current existing one.
    
    repetitive but useful: this transaction came later than current existing one.
    
    new: this transaction never happened before, add this edge in graph.



##Analysis

[Back to Table of Contents] (README.md#table-of-contents)

If there's n nodes in graph, m unique transactions in 60s-window, then:

Each transaction involves two persons of interest.

The minimum nodes in the graph will satisfy: m = n(n-1)/2 => n ~= sqrt(2m)

The maximum nodes in the graph will be n = 2m

<b>Space complexity:</b>

O(m) + O(n)

(60s-window + graph)

<b>Time complexity:</b>

Consider the worst case, if number of expired transactions = d, and each node has k neighbors in average:

Overall = O(1) + O(1) + O(2d)*O(k) + O(nlogn)

(search to find duplicity + search to comprare repetition time + update window + find new median)

The O(2d)*O(k) for update window includes:

    1. Kick out expired transactions, number = d
    2. Fix nodes that involved in expired transactions, number of nodes = 2d. It's O(k) to delete item in python. Worst case: O(2d)*O(k)

The worst case hardly happen. We can safely draw a O(nlogn) time complexity.

Ref: [here] (https://wiki.python.org/moin/TimeComplexity)


##System and Required Packages

[Back to Table of Contents] (README.md#table-of-contents)

Developed with Python 2.7.11

    sys - for file reading and writing.

    datetime - to deal with time format that contained in input file.

    numpy - to seek the median.

##Repo directory structure

[Back to Table of Contents] (README.md#table-of-contents)

Repo Structure

	├── README.md 
	├── run.sh
	├── src
	│  	├── rolling_median_YJL.py
    │   └── median_of_medians.py
	├── venmo_input
	│   ├── test.txt
    │   └── venmo-trans.txt
	├── venmo_output
	│   └── output.txt
    ├── images
    │   ├── flowchart.png
    │   └── status.png
	└── insight_testsuite
	 	   ├── run_tests.sh
		   └── tests
	        	├── test-1-venmo-trans
        		│   ├── venmo_input
        		│   │   └── venmo-trans.txt
        		│   └── venmo_output
        		│       └── output.txt
        		└── temp
            		 ├── venmo_input
            		 │	  └── venmo-trans.txt
            		 └── venmo_output
            			  └── output.txt

##Future Work

[Back to Table of Contents] (README.md#table-of-contents)

According to [here] (https://github.com/numpy/numpy/issues/1811), Numpy uses quicksort which is O(nlogn) on average.

It can be improved into O(n) if we apply "median of medians algorithm".

Based on quickselect algorithm, ["median of medians algorithm"] (https://en.wikipedia.org/wiki/Median_of_medians) is optimal, having worst-case linear time complexity for selecting the kth largest element.

A naive implement is under src/median_of_medians.py, however, it's needs further fine-tuning.


