Quick Navigation

1. [Input and Output] (README.md#input-and-output)

2. [Required Packages] (README.md#required-packages)

3. [Repo directory structure] (README.md#repo-directory-structure)

##Input and Output

[Back to Table of Contents] (README.md#quick-navigation)

Input: a text file containing bunch of transaction datas (with regulated format). 

Output: a text file named 'output.txt' in the 'venmo_output' directory.

##Required Packages
[Back to Table of Contents] (README.md#quick-navigation)

(a) sys - for file reading and writing.

(b) datetime - for dealing with time format that contained in input file.

(c) numpy - for seeking the median.

It's also important to use software engineering best practices like **unit tests**, especially since public data is not clean and predictable. For more details about the implementation, please refer to the FAQ below or email us at <mailto:cc@insightdataengineering.com>

##Repo directory structure
[Back to Table of Contents] (README.md#quick-navigation)

Repo Structure

	├── README.md 
	├── run.sh
	├── src
	│  	└── rolling_median_YJL.py
	├── venmo_input
	│   ├── test.txt
    │   └── venmo-trans.txt
	├── venmo_output
	│   └── output.txt
	└── insight_testsuite
	 	   ├── run_tests.sh
		   └── tests
	        	└── test-1-venmo-trans
        		│   ├── venmo_input
        		│   │   └── venmo-trans.txt
        		│   └── venmo_output
        		│       └── output.txt
        		└── temp
            		 ├── venmo_input
            		 │	  └── venmo-trans.txt
            		 └── venmo_output
            			  └── output.txt
