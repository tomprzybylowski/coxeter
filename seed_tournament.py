# Construction of a tournament of a given kind and score sequence
import numpy as np

# Kind A requests 'win' sequence, while kinds B, C, D request 'score' sequence
# Below code ASSUMES that the sequence is non-negative, decreasing and valid sequence of given kind
# (A-kind does not assume that seq is decreasing)
# Function returns an adjacency matrix
def construct_tournament(seq, kind):
    n = len(seq)
    tournament = np.zeros((n,n))

    ### Kind A returns upper-triangular matrix.
    ### tournament[i,j] == 1 iff i -> j
    if kind == 'A':
        s = [[seq[i],i] for i in range(n)]
        s = sorted(s, key = lambda x: x[0], reverse = True)

        for i in range(n):
            i_index = s[i][1]
            for j in range(i+1,n-s[i][0]):  ### Losses of player s[i][1]
                j_index = s[j][1]
                if i_index < j_index:
                    tournament[i_index,j_index] = -1
                else:
                    tournament[j_index,i_index] = 1
                s[j][0] -= 1
            for j in range(n-s[i][0],n):    ### Wins of player s[i][1]
                j_index = s[j][1]
                if i_index < j_index:
                    tournament[i_index,j_index] = 1
                else:
                    tournament[j_index,i_index] = -1
        return tournament

    elif kind == 'D' or kind == 'C':
        A_win_seq = A_seq_from_score(seq.copy(), kind)   ### This might be non-decreasing!
        tournament = construct_tournament(A_win_seq, 'A')

        for i in range(n):
            for j in range(i+1,n):
                    tournament[j,i] = 1

        if kind == 'C':
            for i in range(n):
                tournament[i,i] = 1

        ### Next loop takes the greater equal A-kind tournament, and
        ### transforms it to C/D kind tournament of desired score seq
        for i in range(n):
            counter = A_win_seq[i] - seq[i]
            if kind == 'C':
                counter += 1
            j = 0
            while counter > 0:
                if i < j:
                    if tournament[i,j] == 1 and tournament[j,i] == 1:
                        tournament[i,j] = -1
                        tournament[j,i] = -1
                        counter -= 2
                elif i > j:
                    if tournament[j,i] == -1 and tournament[i,j] == 1:
                        tournament[j,i] = 1
                        tournament[i,j] = -1
                        counter -= 2
                elif i == j and kind == 'C':
                    if tournament[i,i] == 1:
                        tournament[i,i] = -1
                        counter -= 2
                j += 1

        return tournament

    ### Follows Proof of Thm 4 (if part, kind Bn), Coxeter interchange graphs
    elif kind == 'B':
        if (sum(seq) - n/2 - n*(n-1)/2) % 2 == 0:
            D_seq = (seq.copy() - np.ones(n) / 2).astype(int)
            tournament = construct_tournament(D_seq, 'D')
            for i in range(n):
                tournament[i,i] = 1/2
        else:
            D_seq = (seq.copy() - np.ones(n) / 2).astype(int)
            adj_index = len(D_seq) - 1
            while adj_index > 0:
                if D_seq[adj_index] != D_seq[adj_index - 1]:
                    break
                else:
                    adj_index -= 1
            D_seq[adj_index] += 1
            tournament = construct_tournament(D_seq, 'D')
            for i in range(n):
                if i != adj_index:
                    tournament[i,i] = 1/2
                else:
                    tournament[i,i] = -1/2

        return tournament





### Lemma 8 from the paper Coxeter Interchange Graphs
def A_seq_from_score(seq, kind):
    z = greater_equal(seq.copy(), kind)
    indices = []

    for i in range(len(seq)):
        if (z[i] - seq[i]) % 2 == 1:
            indices.append(i)


    counter = 0
    for i in indices:
        counter += 1
        if counter % 2 == 1:
            z[i] = z[i] - 1
        else:
            z[i] = z[i] + 1

    if kind == 'C':
        for i in range(len(z)):
            z[i] = z[i] - 1


    return z

### Follows Lemma 7 from paper Coxeter Interchange Graphs
def greater_equal(seq, kind):
    n = len(seq)
    if kind == 'C' and sum(seq) == n*(n-1) / 2 + n:
        return seq
    elif kind == 'D' and sum(seq) == n*(n-1) / 2:
        return seq
    else:
        curr_ind = n-1
        while curr_ind > 0:
            if seq[curr_ind-1] > seq[curr_ind]:
                break
            else:
                curr_ind -= 1
        seq[curr_ind] += 1
        return greater_equal(seq, kind)
