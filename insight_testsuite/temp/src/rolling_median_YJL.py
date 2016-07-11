"""
Insight data engineer challenge
(Yun-Jun Lee)

This challenge requires you to:

1. Use Venmo payments that stream in to build a graph of users and their relationship with one another.
2. Calculate the median degree of a vertex in a graph and update this each time a new Venmo payment appears.
   You will be calculating the median degree across a 60-second sliding window.

The vertices on the graph represent Venmo users and whenever one user pays another user,
an edge is formed between the two users.

"""
import sys
import datetime
import numpy

def rolling_med(transactions, output):
    """
    Input:
    transactions is a list that contains all records as dictionary, 
    transactions = ['created_time', 'poi_a', 'poi_b']
    created_time: How many seconds from transaction time to reference time
    poi: sorted actor/target pair => therefore, Mary/Andy and Andy/Mary will have the same order.
    
    graph: a dictionary to represent graph info, (key = name of node, value = node)
    window: a queue to record transactions in the rolling window.

    For each transaction:
    1. build edge - refer to make_edge()
    2. update the transaction window
    2. cut edges - refer to cut_edge()
    3. return the median degree.
    """
    class Logger(object):
        def __init__(self, filename="Default.log"):
            self.terminal = sys.stdout
            self.log = open(filename, "a")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

    class Node(object):
        """
        Class of a Node

        For each node, record its:
        0. name (person of interest)
        1. number of connected edges
        2. counterparts that connected to
        3. expiring time of each edge
        4. expiring time of itself
        """
        def __init__(self, node):
            self.name = node
            self.neighbors = {}     # key = name of neighbors, value = expiring time
            self.num_of_edges = 0   # number of connected edges

        def __repr__(self):
            return '%s, %d' % (self.name, self.num_of_edges)

    def make_edge(endtime, graph, window, single_transaction, new_median):
        """
        Construct a new edge

        0. First, check if this transaction is valid, duplicated, or not.

        if valid:
        (The ONLY situation we need to find a new median later)
        1. initialize two nodes (if necessary)
        2. construct the edge between two nodes
        3. calculate the median degree of vertex
        
        input -
        endtime: the latest transaction in current window
        graph: graph of current window
        window: transaction queue in current window
        single_transaction
        """

        transac_time = single_transaction[0]
        poi_a = single_transaction[1]
        poi_b = single_transaction[2]
        exp_time = transac_time + 60

        nodes_in_window = [nd.name for nd in graph]
        # initialize the node if necessary
        if poi_a not in nodes_in_window:
            graph.append(Node(poi_a))
        if poi_b not in nodes_in_window:
            graph.append(Node(poi_b))

        nodes_in_window = [nd.name for nd in graph]     # get nodes again
        index_a = nodes_in_window.index(poi_a)
        index_b = nodes_in_window.index(poi_b)

        ## print "transac_time", type(transac_time), transac_time, "exp_time", type(exp_time), exp_time

        # Not valid
        if (endtime - transac_time) > 60:
            new_median = False
            ##print "out of window, arrive too late"
            ## print "endtime:", endtime, "transac_time", transac_time
            return endtime

        # duplicated and newer
        if poi_b in nodes_in_window and poi_a in graph[index_b].neighbors.keys():    # a & b are linked
            new_median = False
            ##print "duplicated transaction"
            assert poi_a in nodes_in_window and poi_b in graph[index_a].neighbors.keys()
            earlier_transac_time = graph[index_b].neighbors[poi_a]-60
            if transac_time > earlier_transac_time:             # if this transaction happens later
                ##print "Valid: update the graph"
                ##temp = 0
                for x in window:                                # update the window
                    if x[1] == poi_a and x[2] == poi_b:
                        assert (x[0] < single_transaction[0])
                        ##print "remove:", x
                        ##temp = x[0]
                        window.remove(x)
                window.append(single_transaction)
                ##print "append:", single_transaction, "+", single_transaction[0]-temp, 'sec'

                graph[index_b].neighbors[poi_a] = exp_time        # update the graph
                graph[index_a].neighbors[poi_b] = exp_time

            ##else: print "Invalid transaction (duplicated and outdated)"
            return max(transac_time, endtime)

        # Valid
        ##print "valid transaction"
        else:
            new_median = True
            window.append(single_transaction)

            # construct the edge (update the info in each node)
            graph[index_a].neighbors[poi_b] = exp_time
            graph[index_a].num_of_edges += 1
            graph[index_b].neighbors[poi_a] = exp_time
            graph[index_b].num_of_edges += 1

            return max(transac_time, endtime)

    def cut_edge(endtime, graph, sorted_window):
        """
        Cut these edges formed more than 1 min since the latest transaction time.

        First, for each transactions should be removed, cut the corresponding edge:
        1. fix poi_a
        2. fix poi_b
        
        Next, remove expired transactions (by del)
        """
        starttime = endtime - 60
        cut = 0

        name_list = []

        while sorted_window[cut][0] < starttime:

            nodes_in_window = [nd.name for nd in graph]
            ##print "current window:", starttime, " to ", endtime
            ##print "need to go:", sorted_window[cut]

            poi_a = sorted_window[cut][1]
            poi_b = sorted_window[cut][2]

            if poi_a not in name_list:
                name_list.append(poi_a)
            if poi_b not in name_list:
                name_list.append(poi_b)

            ##print poi_a
            ##print poi_b

            index_a = index_b = 0
            if poi_a in nodes_in_window:
                index_a = nodes_in_window.index(poi_a)
            if poi_b in nodes_in_window:
                index_b = nodes_in_window.index(poi_b)

            ##print "cut who", graph[index_a], graph[index_a].neighbors, endtime
            ##print "cut who", graph[index_b], graph[index_b].neighbors, endtime
            #assert graph[index_a].neighbors[poi_b] < endtime

            del graph[index_a].neighbors[poi_b]
            graph[index_a].num_of_edges -= 1
            del graph[index_b].neighbors[poi_a]
            graph[index_b].num_of_edges -= 1

            if graph[index_a].num_of_edges == 0 and graph[index_b].num_of_edges == 0:
                ##print "say goodbye to both of them"
                del graph[max(index_a, index_b)]
                del graph[min(index_a, index_b)]
            elif graph[index_a].num_of_edges == 0 or graph[index_b].num_of_edges == 0:
                ##print "say goodbye to one of them"
                if graph[index_a].num_of_edges == 0:
                    del graph[index_a]
                else:
                    del graph[index_b]
            ##print "cut!"
            ##print "now", graph[index_a], graph[index_a].neighbors, endtime
            ##print "now", graph[index_b], graph[index_b].neighbors, endtime
            cut += 1

        sorted_window = [sorted_window[i] for i in xrange(len(sorted_window)) if i >= cut]
        ##print "Window after cutting:", sorted_window
        return sorted_window

############################################################
    sys.stdout = Logger(output)

    graph = []              # lsit of node
    window = []
    endtime = transactions[0][0] + 60
    new_median = True
    median = 0
    ##print "init:", endtime

    for i in xrange(len(transactions)):
        temp = endtime
        #before adding edge(graph):", len(graph)
        endtime = make_edge(endtime, graph, window, transactions[i], new_median)
        ##print "after adding (graph):", len(graph)

        assert endtime >= temp
        if endtime > temp:
            ##print "before cutting (graph):", len(graph)
            window = cut_edge(endtime, graph, sorted(window))
            ##print "after cutting (graph):", len(graph)

        # output the median of graph.values()
        ##print [nd.num_of_edges for nd in graph]
        if new_median:
            median = numpy.median([nd.num_of_edges for nd in graph])
            print "%.2f" % median
        else:
            print median

############################################################
if __name__ == '__main__':
    FILE = open(sys.argv[1])            # txt file that containing records
    OUTPUT = sys.argv[2]
    TRANS_REC = []                      # transaction records

    # check this for time format:       https://www.w3.org/TR/NOTE-datetime
    # Here we use only "Seconds to reference time" as time unit.
    first_line = eval(FILE.readline())
    ref_time = datetime.datetime.strptime(first_line['created_time'], '%Y-%m-%dT%H:%M:%SZ')
    TRANS_REC.append(sorted([0, first_line['actor'], first_line['target']]))
    

    for line in FILE:                   # Read them all
        newdict = eval(line)            # Since it's already in dictionary format, just read as dic
        trans_time = datetime.datetime.strptime(newdict['created_time'], '%Y-%m-%dT%H:%M:%SZ')
        newdict['created_time'] = (trans_time - ref_time).total_seconds()
        TRANS_REC.append(sorted(newdict.values()))

    rolling_med(TRANS_REC, OUTPUT)