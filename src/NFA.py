from .DFA import DFA
from collections import deque
from dataclasses import dataclass
from collections.abc import Callable
from typing import Optional


EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]
    Tokens: Optional[dict[STATE, str]] = None

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file

        # check if the state is defined
        # if state not in self.K:
        #     return set()

        reachable_states : set[STATE]
        reachable_states = set()
        current_state : STATE

        # queue for states
        queue = deque()
        queue.append(state)

        # pop a state and search for all the next epsilon reachable states
        while queue:
            current_state = queue.pop()
            if current_state in reachable_states:
                continue
            else:
                reachable_states.add(current_state)

            # check if the transition exists
            transition = (current_state, EPSILON) 
            if transition in self.d:
                next_states = self.d[transition]

                for aux_state in next_states:
                    queue.append(aux_state)

            
        return reachable_states

    def subset_construction(self) -> DFA[frozenset[STATE]]:  
        # convert this nfa to a dfa using the subset construction algorithm
        # DFA
        dfa : DFA[frozenset[STATE]]
        
        current_state : frozenset[STATE]
        start_state : frozenset[STATE]
        sink_state : frozenset[STATE]

        start_state = frozenset(self.epsilon_closure(self.q0))
        sink_state = frozenset("sink")

        dfa_S = self.S
        dfa_K = set()
        dfa_d = {}
        # for symbol in self.S:
        #     transition = (sink_state, symbol)
        #     dfa_d[transition] = sink_state
        dfa_q0 = start_state
        dfa_F = set()
        Tokens = {}
        
        for aux_F in self.F:
            if aux_F in start_state:
                dfa_F.add(start_state)

        # queue for states
        queue = deque()
        queue.append(start_state)

        while queue:
            current_state = queue.pop()
            
            if current_state in dfa_K:
                continue
            else:
                dfa_K.add(current_state)

            # create new states for each symbol
            for symbol in self.S:
                next_state = set()

                # get all the next transitions for the current symbol
                for aux_state in current_state:
                    transition = (aux_state, symbol) 
                    if transition in self.d:
                        next_state.update(self.d[transition])

                next_state_epsilon = set()
                # get epsilon closure
                for aux_state in next_state:
                    next_state_epsilon.update(self.epsilon_closure(aux_state))
                next_state.update(next_state_epsilon)

                next_state_frozen = frozenset(next_state)
                if next_state_frozen:
                    transition = (current_state, symbol)
                    dfa_d[transition] = next_state_frozen

                    for aux_F in self.F:
                        if aux_F in next_state_frozen:
                            dfa_F.add(next_state_frozen)

                    # create the new dictionary for final state - regex token
                    if self.Tokens:
                        for key_Token, val_token in self.Tokens.items():
                            if key_Token in next_state_frozen:
                                Tokens[next_state_frozen] = val_token

                    queue.append(next_state_frozen)
                else:
                    if "sink" not in dfa_K: 
                        for symbol_aux in self.S:
                            transition = (sink_state, symbol_aux)
                            dfa_d[transition] = sink_state
                        dfa_K.add(sink_state)
                    transition = (current_state, symbol)
                    dfa_d[transition] = sink_state

        dfa = DFA(dfa_S, dfa_K, dfa_q0, dfa_d, dfa_F, Tokens)
        return dfa

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        new_dfa : NFA[OTHER_STATE]
        new_S = self.S
        new_K = set()
        new_d = {}
        new_F = set()

        mapping = {}

        for state in self.K:
            mapping[state] = f(state)
            new_K.add(mapping[state])
        new_q0 = mapping[self.q0]

        for transition in self.d:
            new_d[(mapping[transition[0]], transition[1])] = {mapping[state] for state in self.d[transition]}

        for final_state in self.F:
            new_F.add(mapping[final_state])
        

        new_nfa = NFA(new_S, new_K, new_q0, new_d, new_F)

        return new_nfa
