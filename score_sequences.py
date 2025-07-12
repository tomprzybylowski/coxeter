######### Finding all possible score (win) sequences of Coxeter tournaments

from itertools import combinations_with_replacement, product
import numpy as np
import ig
import networkx as nx



def is_majorized(x, y, weakly):
    """ Return True if x is majorized by y.
    Weakly = False requires further sum(x) == sum(y) """

    sorted_x = sorted(x, reverse=True) # Sorted in decreasing order
    sorted_y = sorted(y, reverse=True)

    if len(x) != len(y):
        raise ValueError("Lengths of vectors are distinct!")

    # Check the prefix sums condition
    prefix_sum_x = 0
    prefix_sum_y = 0
    for i in range(len(x)):
        prefix_sum_x += sorted_x[i]
        prefix_sum_y += sorted_y[i]
        if prefix_sum_x > prefix_sum_y:
            return False
    if weakly == True or prefix_sum_x == prefix_sum_y:
        return True
    else:
        return False


def majorized_sequences(s, weakly):
    """ Return a list of non-negative non-increasing sequences which are majorized
    by sequence s """

    # List to store all weakly-majorized sequences
    result = []

    n = len(s)
    max_val = max(s)

    # Generate all possible non-increasing sequences of length n
    possible_sequences = combinations_with_replacement(range(max_val + 1), n)

    # Check each non-increasing sequence if it is weakly-majorized by s
    for candidate in possible_sequences:
        candidate = sorted(candidate, reverse=True)  # Ensure the sequence is non-increasing
        if is_majorized(candidate, s, weakly):
            result.append(candidate)

    # Remove duplicates and sort the result
    result = [list(seq) for seq in set(tuple(seq) for seq in result)]

    return result


# Lists all non-negative score sequences of a given length and kind
### FOR kind 'A' returns a list of win sequences!
def score_sequences(n, kind):
    if kind == 'A':
        transitive_seq = [n-i-1 for i in range(n)]
        result = majorized_sequences(transitive_seq, False)
    elif kind == 'D':
        transitive_seq = [n-i-1 for i in range(n)]
        parity = sum(transitive_seq) % 2
    elif kind == 'C':
        transitive_seq = [n-i for i in range(n)]
        parity = sum(transitive_seq) % 2
    elif kind == 'B':
        transitive_seq = [n-i-1/2 for i in range(n)]
        D_scores = score_sequences(n, 'D')
        result = []
        for half_edges_seq in product([-1/2, 1/2], repeat=n):
            for seq in D_scores:
                seq2 = np.array(seq) + np.array(half_edges_seq)
                if np.all(seq2 > 0):
                    result.append(sorted(seq2, reverse=True))
        result = set(tuple(seq) for seq in result)
        result = [list(seq) for seq in result]

    if kind == 'C' or kind == 'D':
        result = []
        for seq in majorized_sequences(transitive_seq, True):
            if sum(seq) % 2 == parity:
                result.append(seq)

    return result

### A sequence is irreducible if when sorted, comparing its partial sums with the 
### partial sums of the transitive sequence, it is not possible to find a pair of indices
### such that the partial sum of the sequence is less than the partial sum of the transitive sequence.
def is_irreducible(seq, kind):
    """ Check if a score sequence is irreducible for a given kind """
    if kind not in ['A', 'B', 'C', 'D']:
        raise ValueError("Invalid kind. Must be one of 'A', 'B', 'C', or 'D'.")
    if kind == 'A':
        transitive_seq = [len(seq) - i - 1 for i in range(len(seq))]
    elif kind == 'D':
        transitive_seq = [len(seq) - i - 1 for i in range(len(seq))]
    elif kind == 'C':
        transitive_seq = [len(seq) - i for i in range(len(seq))]
    elif kind == 'B':
        transitive_seq = [len(seq) - i - 1/2 for i in range(len(seq))]

    transitive_prefix_sums = np.cumsum(transitive_seq)
    seq_prefix_sums = np.cumsum(seq)

    for i in range(len(seq) - 1):
        if seq_prefix_sums[i] == transitive_prefix_sums[i]:
            return False

    return True



def save_to_file(kinds, ns, add=False):
    """ Save all possible score sequences of given kinds and lengths to file """

    if add:
        mode = 'a'
    else:
        mode = 'w'

    with open("sequences.txt", mode) as f:
        for kind in kinds:
            for n in ns:
                seqs = score_sequences(n, kind)
                f.write(f"{kind} {n} {'; '.join(map(str, seqs))}\n")



####################################
### Adding more info to the file with score sequences
### Add number of nodes and edges to the file
### Abort adding if a graph has too many vertices
#####################################
def add_info_to_file(filename="sequences.txt", abort=False, abort_threshold=200):
    with open(filename, 'r') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        parts = line.strip().split(None, 2)
        if len(parts) != 3:
            new_lines.append(line)
            continue
        line_type, line_players, line_seq = parts
        try:
            for seq in line_seq.split(";"):
                seq = eval(seq)
                n = len(seq)
                graph = ig.interchange_graph(list(seq), line_type, abort=abort, abort_threshold=abort_threshold)
                if graph is None:
                    print(f"Skipping sequence {seq} due to graph creation failure.")
                    continue
                num_nodes = graph.number_of_nodes()
                num_edges_of_type_C = len([edge for edge in graph.edges(data=True) if edge[2]['kind'] == 'C'])
                num_edges = graph.number_of_edges() + num_edges_of_type_C
                irreducible = is_irreducible(seq, line_type)
                if irreducible:
                    new_lines.append(f"{line_type};{line_players};{seq};{num_nodes};{num_edges}\n")
                #print(f"Processed sequence: {seq}, Number of nodes: {num_nodes}, Number of edges: {num_edges}")
        except Exception as e:
            print(f"Error processing line: {line} - {e}")
            new_lines.append(line)

    # Save the modified lines back to the new file
    new_filename = filename.replace(".txt", "_with_info.txt")
    with open(new_filename, 'w') as f:
        f.writelines(new_lines)
    print(f"Added number of nodes and edges to {new_filename}")