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
    1. check its validity
    2. check its duplicity
    3. update the graph (if necessary)
    4. update the window (if necessary)
    5. find the new median (or use the old one)
    """

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

    def validity(endtime, single_transaction):
        """
        Check whether this transaction is invalid or valid

        Return: boolean value
        """
        transac_time = single_transaction[0]
        return (endtime-60 <= transac_time)

    def duplicity(endtime, graph, window, single_transaction, new_median):
        """
        Check whether this transaction will make a new_edge or not

        Return: new endtime (if has any)
        """
        transac_time = single_transaction[0]
        poi_a = single_transaction[1]
        poi_b = single_transaction[2]

        nodes_in_window = [nd.name for nd in graph]
        index_a = index_b = 0

        if poi_a in nodes_in_window and poi_b in nodes_in_window: 
            index_a = nodes_in_window.index(poi_a)
            index_b = nodes_in_window.index(poi_b)

        duplicated = (poi_b in nodes_in_window and poi_a in graph[index_b].neighbors.keys())

        if duplicated:

            new_median = False          # need to find new median only when endtime is updated
            the_other_transac_time = graph[index_b].neighbors[poi_a]-60

            if transac_time > the_other_transac_time:             # if later than the earlier one...

                for x in window:                                # ...update the window
                    if x[1] == poi_a and x[2] == poi_b:
                        assert (x[0] <= single_transaction[0])
                        window.remove(x)                        # ...remove the earlier one
                window.append(single_transaction)               # ...and add this new one

                if transac_time > endtime:                      # if even later than endtime...
                    new_median = True                           # ...need to cut some more edges

            return max(transac_time, endtime)

        return False

    def make_edge(endtime, graph, window, single_transaction, new_median):
        """
        Construct a new edge for a valid transaction

        check whether there's a duplicated situation.

        1. initialize two nodes (if necessary)
        2. construct the edge between two nodes
        3. calculate the median degree of vertex
        
        input -
        endtime: the latest transaction in current window
        graph: graph of current window
        window: transaction queue in current window
        single_transaction
        """
        new_median = True                       # Definitely need to find new median

        transac_time = single_transaction[0]
        exp_time = transac_time + 60
        poi_a = single_transaction[1]
        poi_b = single_transaction[2]
        
        index_a = index_b = 0

        nodes_in_window = [nd.name for nd in graph]

        # initialize the node if necessary
        if poi_a not in nodes_in_window:
            graph.append(Node(poi_a))
            nodes_in_window.append(poi_a)       # need to update name list
        if poi_b not in nodes_in_window:
            graph.append(Node(poi_b))
            nodes_in_window.append(poi_b)       # need to update name list

        index_a = nodes_in_window.index(poi_a)
        index_b = nodes_in_window.index(poi_b)

        window.append(single_transaction)

        # construct the edge (update the info in each node)
        graph[index_a].neighbors[poi_b] = exp_time
        graph[index_a].num_of_edges += 1
        graph[index_b].neighbors[poi_a] = exp_time
        graph[index_b].num_of_edges += 1

        return max(transac_time, endtime)

    def cut_edge(endtime, graph, sorted_window, new_median):
        """
        Cut these edges formed more than 1 min since the latest transaction time.

        In graph, fix both nodes involving in the expired transaction.
        Check transactions one by one in window from oldest, and stop when still un-expire.
        
        In window, remove expired transactions (by del)
        """
        starttime = endtime - 60
        cut = 0                                         # The index of transaction in window

        # In graph
        while sorted_window[cut][0] < starttime:        # for each transaction ...

            new_median = True 

            poi_a = sorted_window[cut][1]               # get name of both nodes that involving in,
            poi_b = sorted_window[cut][2]

            nodes_in_window = [nd.name for nd in graph] # from all we have in graph,
            index_a = nodes_in_window.index(poi_a)      # get their index.
            index_b = nodes_in_window.index(poi_b)

            del graph[index_a].neighbors[poi_b]         # (1) remove b from a's neighbor
            graph[index_a].num_of_edges -= 1            # (2) a's number of connected edge - 1
            del graph[index_b].neighbors[poi_a]
            graph[index_b].num_of_edges -= 1

            # If anyone of them is now having no neighbors => DELETE THEM
            if graph[index_a].num_of_edges == 0 and graph[index_b].num_of_edges == 0:
                del graph[max(index_a, index_b)]
                del graph[min(index_a, index_b)]
            elif graph[index_a].num_of_edges == 0 or graph[index_b].num_of_edges == 0:
                if graph[index_a].num_of_edges == 0:
                    del graph[index_a]
                else:
                    del graph[index_b]

            cut += 1                                    # Go to next expiring transaction

        # In window
        sorted_window = [sorted_window[i] for i in xrange(len(sorted_window)) if i >= cut]
        return sorted_window

############################################################

    graph = []              # list of node
    window = []             # list of transaction
    endtime = transactions[0][0] + 60
    median = 0

    for i in xrange(len(transactions)):                 # For each transaction ...
        new_median = True
        temp = endtime

        if not validity(endtime, transactions[i]):      # if it's expired ...
            new_median = False                          # ... no need to find new_median.

        else:                                           # if it's not expired ...
            repeat = duplicity(endtime, graph, window, transactions[i], new_median)

            # The endtime of window could need renew, no matter it's repeated or not.
            if repeat:
                endtime = repeat
            else:
                endtime = make_edge(endtime, graph, window, transactions[i], new_median)

            # If the endtime has changed => update the window
            if endtime > temp:
                window = cut_edge(endtime, graph, sorted(window), new_median)

            # If the graph has changed => find new median
            if new_median:
                median = numpy.median([nd.num_of_edges for nd in graph])
            
        output.write("%.2f\n" % (median))

    return

############################################################
if __name__ == '__main__':
    INPUT = open(sys.argv[1], 'r')      # txt file that containing transaction records
    OUTPUT = open(sys.argv[2], 'w')
    TRANS_REC = []                      # transaction records

    ref_time = 0
    
    for line in INPUT:                  # Read them all
        newdict = eval(line)            # Since it's already in dictionary format, just read as dic
        if not TRANS_REC:
            ref_time = datetime.datetime.strptime(newdict['created_time'], '%Y-%m-%dT%H:%M:%SZ')
            TRANS_REC.append(sorted([0, newdict['actor'], newdict['target']]))
        else:
            trans_time = datetime.datetime.strptime(newdict['created_time'], '%Y-%m-%dT%H:%M:%SZ')
            newdict['created_time'] = (trans_time - ref_time).total_seconds()
            TRANS_REC.append(sorted(newdict.values()))

    rolling_med(TRANS_REC, OUTPUT)

    INPUT.close()
    OUTPUT.close()