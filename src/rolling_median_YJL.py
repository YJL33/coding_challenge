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

            new_median = False          # need to find new median only when on very special case
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
        index_a = -1
        index_b = -1

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
    ##sys.stdout = Logger(output)

    graph = []              # list of node
    window = []             # list of transaction
    endtime = transactions[0][0] + 60
    median = 0
    ##print "init:", endtime

    for i in xrange(len(transactions)):
        new_median = True
        temp = endtime

        if not validity(endtime, transactions[i]):
            ##print "invalid transaction"
            output.write("%.2f\n" % (median))

        else:
            dupe = duplicity(endtime, graph, window, transactions[i], new_median)

            if dupe:
                endtime = dupe
                ##print "duplicated, endtime = ", endtime
            else:
                endtime = make_edge(endtime, graph, window, transactions[i], new_median)
                ##print "new edge, endtime = ", endtime

            if endtime > temp:
                ##print "kick out somebody!"
                window = cut_edge(endtime, graph, sorted(window))

            if new_median:
                median = numpy.median([nd.num_of_edges for nd in graph])
                output.write("%.2f\n" % (median))
            else:
                output.write("%.2f\n" % (median))

    return

############################################################
if __name__ == '__main__':
    INPUT = open(sys.argv[1], 'r')            # txt file that containing records
    OUTPUT = open(sys.argv[2], 'w')
    TRANS_REC = []                      # transaction records

    # check this for time format:       https://www.w3.org/TR/NOTE-datetime
    # Here we use only "Seconds to reference time" as time unit.
    first_line = eval(INPUT.readline())
    ref_time = datetime.datetime.strptime(first_line['created_time'], '%Y-%m-%dT%H:%M:%SZ')
    TRANS_REC.append(sorted([0, first_line['actor'], first_line['target']]))

    for line in INPUT:                   # Read them all
        newdict = eval(line)            # Since it's already in dictionary format, just read as dic
        trans_time = datetime.datetime.strptime(newdict['created_time'], '%Y-%m-%dT%H:%M:%SZ')
        newdict['created_time'] = (trans_time - ref_time).total_seconds()
        TRANS_REC.append(sorted(newdict.values()))

    rolling_med(TRANS_REC, OUTPUT)
    INPUT.close()
    OUTPUT.close()