from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
import pandas as pd
from typing import TypeVar
from functools import reduce
from collections import deque
from typing import Optional

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]
    Tokens: Optional[dict[STATE, str]] = None

    def accept(self, word: str) -> bool:
        # check for empty string
        if not word:
            return self.q0 in self.F
        
        current_state = self.q0
        
        # iterate through the imput
        for symbol in word:
            # check if the symbol exists in the alphabet
            if symbol not in self.S:
                return False
            
            # check if the transition exists
            transition = (current_state, symbol) 
            if transition in self.d:
                current_state = self.d[transition]
            else:
                return False
            
        # check if the state is a final state
        if current_state in self.F:
            if current_state in self.Tokens:
                return self.Tokens[current_state]
            return current_state
        return False
        return current_state in self.F
    
    
    def minimize(self) -> 'DFA[STATE]':
        # get the predecessors of each state
        inversed_d = {}
        for key, value in self.d.items():
            if (value, key[1]) not in inversed_d :
                inversed_d[(value, key[1])] = []
            inversed_d[(value, key[1])].append(key[0])
        
        queue = deque()
        N = len(self.K)

        # create mapping from set to index
        states = list(self.K)
        state_to_idx = {}
        for i in range(N):
            state_to_idx[states[i]] = i
        for i in range(N):
            state_to_idx[i] = states[i]

        # create the distinguishable matrix
        matrix = []
        for i in range(N):
            row = []
            for j in range(N):
                row.append(0)
            matrix.append(row)

        # base case
        for i in range(1, N):
            for j in range(i):
                if (states[i] in self.F) != (states[j] in self.F):
                    matrix[i][j] = 1
                    queue.append((i, j))

        while queue:
            pair = queue.pop()

            # check if the pair was already visited
            if matrix[pair[0]][pair[1]] == 2:
                continue
            matrix[pair[0]][pair[1]] = 2

            # mark the predecessors
            for symbol in self.S:
                states_pair0 = []
                states_pair1 = []

                # get the predecessors for each element of the pair
                key_val = (states[pair[0]], symbol)
                states_pair0 = inversed_d.get(key_val, [])
                key_val = (states[pair[1]], symbol)
                states_pair1 = inversed_d.get(key_val, [])

                for i in states_pair0:
                    for j in states_pair1:
                        idx_1 = state_to_idx[i]
                        idx_2 = state_to_idx[j]

                        # fill only the bottom of the matrix
                        if (idx_1 < idx_2):
                            aux = idx_1
                            idx_1 = idx_2
                            idx_2 = aux

                        if (matrix[idx_1][idx_2] == 0):
                            matrix[idx_1][idx_2] = 1
                            queue.append((idx_1, idx_2))

        # search for indistinguishable groups of states
        group_states = []
        for j in range(N - 1):
            group_line = set()
            for i in range(j + 1 , N):
                if matrix[i][j] == 0:
                    group_line.add(states[i])
                    group_line.add(states[j])
            if group_line:
                group_states.append(list(group_line))

        # assign a main value for the group
        main_state = {}
        for subgroup in group_states:
            if subgroup[0] not in main_state:
                for aux in subgroup:
                    main_state[aux] = subgroup[0]
            else:
                main = main_state[subgroup[0]]
                for aux in subgroup:
                    main_state[aux] = main
        
        # add an entry for each state that is a standalone value (isn't a part of a group of states)
        for state in self.K:
            if state not in main_state:
                main_state[state] = state

        new_dfa_S = self.S
        new_dfa_K = set()
        new_dfa_d = {}
        new_dfa_F = set()

        # add the start state
        new_dfa_q0 = main_state.get(self.q0)
        new_dfa_K.add(new_dfa_q0)

        # add the final states
        for final_state in self.F:
            new_dfa_F.add(main_state.get(final_state))

        # add the transitions
        for (state, symbol), dest_state in self.d.items():
            src_state = main_state.get(state)
            rep_dest_state = main_state.get(dest_state)
            
            new_dfa_d[(src_state, symbol)] = rep_dest_state
            new_dfa_K.add(src_state)
            new_dfa_K.add(rep_dest_state)

        return DFA(new_dfa_S, new_dfa_K, new_dfa_q0, new_dfa_d, new_dfa_F)
        