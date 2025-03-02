from typing import Any, List
from .NFA import NFA
from dataclasses import dataclass

EPSILON = ''
current_state = 0

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')


@dataclass
class Void(Regex):
    
    def thompson(self):
        return NFA(set(), set({0}), 0, {}, set())

@dataclass
class Empty(Regex):

    def thompson(self):
        return NFA(set(), set({0}), 0, {}, set({0}))

@dataclass
class Symbol(Regex):
    symbol: str

    def thompson(self):
        global current_state

        start_state = 0
        end_state =  1

        S = set(self.symbol)
        K = set({start_state, end_state})
        q0 = start_state
        d = {(start_state, self.symbol): {end_state}}
        F = set({end_state})
        

        return NFA(S, K, q0, d, F)

@dataclass
class Concat(Regex):
    e1: Regex
    e2: Regex

    def thompson(self):
        NFA_e1 = self.e1.thompson()
        NFA_e2 = self.e2.thompson()

        # remap states from 0 to N (number of states)
        NFA_e1 = NFA_e1.remap_states(lambda state: state - min(NFA_e1.K))
        NFA_e2 = NFA_e2.remap_states(lambda state: state - min(NFA_e2.K) + max(NFA_e1.K) + 1)

        S = NFA_e1.S | NFA_e2.S
        K = NFA_e1.K | NFA_e2.K
        q0 = NFA_e1.q0
        d = NFA_e1.d | NFA_e2.d

        for final_q in NFA_e1.F:
            d.update({(final_q, EPSILON): {NFA_e2.q0}})

        F = NFA_e2.F

        return NFA(S, K, q0, d, F)
    
@dataclass
class Union(Regex):
    e1: Regex
    e2: Regex

    def thompson(self):
        NFA_e1 = self.e1.thompson()
        NFA_e2 = self.e2.thompson()

        # remap states from 1 to N - 1, 0 is the new q0 and N is the new F
        NFA_e1 = NFA_e1.remap_states(lambda state: state - min(NFA_e1.K) + 1)
        NFA_e2 = NFA_e2.remap_states(lambda state: state - min(NFA_e2.K) + max(NFA_e1.K) + 1)

        q0 = 0
        F = {max(NFA_e2.K) + 1}

        S = NFA_e1.S | NFA_e2.S
        K = set({q0}) | NFA_e1.K | NFA_e2.K | set(F)
        d = NFA_e1.d | NFA_e2.d

        d.update({(q0, EPSILON): set({NFA_e1.q0, NFA_e2.q0})})

        for old_F in NFA_e1.F | NFA_e2.F:
            d.update({(old_F, EPSILON) : F.copy()})

        return NFA(S, K, q0, d, F)

@dataclass
class Star(Regex):
    e: Regex

    def thompson(self):
        NFA_e = self.e.thompson()

        # remap states from 1 to N - 1, 0 is the new q0 and N is the new F
        NFA_e = NFA_e.remap_states(lambda state: state - min(NFA_e.K) + 1)

        q0 = 0
        F = {max(NFA_e.K) + 1}
        

        S = NFA_e.S
        K = set({q0}) | NFA_e.K | set(F)
        d = NFA_e.d

        d.update({(q0, EPSILON): {NFA_e.q0}})
        d[(q0, EPSILON)].update(F)

        for old_F in NFA_e.F:
            d.update({(old_F, EPSILON): F.copy()})
            d[(old_F, EPSILON)].update(set({NFA_e.q0}))

        return NFA(S, K, q0, d, F)

@dataclass
class Plus(Regex):
    e: Regex

    def thompson(self):
        return Concat(self.e, Star(self.e)).thompson()

@dataclass
class Question(Regex):
    e: Regex

    def thompson(self):
        return Union(self.e, Symbol(EPSILON)).thompson()


# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex
    

def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string

    # you can define additional classes and functions to help with the parsing process

    # the checker will call this function, then the thompson method of the generated object. the resulting NFA's
    # behaviour will be checked using your implementation form stage 1


    if not regex:
        return Empty()
    
    # strip white spaces that are not before '\'
    while regex[0] == ' ':
        regex = regex[1:]

        if not regex:
            return Empty()

    # left derivation, higher -> lower priority: *, ?, +, concat, |, ()
    if regex[0] == '(':
        parens = 1
        i = 1

        # check if there isn't anything after the parenthesis
        while i < len(regex) and parens != 0:
            if regex[i] == '(':
                parens = parens + 1
            if regex[i] == ')':
                parens = parens - 1
            i = i + 1
        if i >= len(regex):
            # strip the parens
            return parse_regex(regex[1:-1])

        
        # remove white spaces after parens
        while i < len(regex) and regex[i] == ' ':
            regex = regex[:i] + regex[i+1:]

            if i - 1 == len(regex):
                 # strip the parens
                return parse_regex(regex[1:-1])

        if i < len(regex):
            # check the operations in order
            #Union
            j = i
            parens = 0
            while j < len(regex):
                if regex[j] == '(':
                    parens = parens + 1
                if regex[j] == ')':
                    parens = parens - 1
                if regex[j] == '|' and parens == 0:
                    return Union(parse_regex(regex[0:j]), parse_regex(regex[j+1:]))
                j = j + 1
            
            # Concat
            j = i
            while j < len(regex):
                if regex[j] not in "?*+":
                    return Concat(parse_regex(regex[0:j]), parse_regex(regex[j:]))
                j = j + 1
            
            if i + 1 >= len(regex):
                if regex[i] == '*':
                    return Star(parse_regex(regex[1:i-1]))
                if regex[i] == '?':
                    return Question(parse_regex(regex[1:i-1]))
                if regex[i] == '+':
                    return Plus(parse_regex(regex[1:i-1]))

    # check for escaping
    if len(regex) > 1:
        if regex[0] == '\\':
            # remove white spaces after symbol
            while len(regex) > 2 and regex[2] == ' ':
                regex = regex[0:2] + regex[3:]

                if len(regex) == 1:
                    return Symbol(regex[0])

            if len(regex) >= 3:
                # Union
                i = 2
                parens = 0
                while i < len(regex):
                    if regex[i] == '(':
                        parens = parens + 1
                    if regex[i] == ')':
                        parens = parens - 1
                    if regex[i] == '|' and parens == 0:
                        return Union(parse_regex(regex[:i]), parse_regex(regex[i+1:]))
                    i = i + 1
                
                # Concat
                i = 2
                while i < len(regex):
                    if regex[i] not in "?*+":
                        return Concat(parse_regex(regex[:i]), parse_regex(regex[i:]))
                    i = i + 1
 
            if len(regex) == 3:
                if regex[2] == '*':
                    return Star(Symbol(regex[1]))
                if regex[2] == '?':
                    return Question(Symbol(regex[1]))
                if regex[2] == '+':
                    return Plus(Symbol(regex[1]))

            return Symbol(regex[1])
        
        if regex == "[A-Z]":
            return parse_regex("A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z")
        
        if regex == "[a-z]":
            return parse_regex("a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z")
        
        if regex == "[0-9]":
            return parse_regex("0|1|2|3|4|5|6|7|8|9")
        
        if regex == "eps":
            return parse_regex("")

        # check for syntactic sugars
        i = 1
        aux = regex[:5]
        if len(aux) == 5 and (aux == "[A-Z]" or aux == "[a-z]" or aux == "[0-9]"):
            i = 5

        aux = regex[:3]
        if len(aux) == 3 and aux == "eps":
            i = 3
        
        j = i

        # remove white spaces after symbol
        while len(regex) > i and regex[j] == ' ':
            regex = regex[:j] + regex[j+1:]

            if len(regex) == 1:
                return Symbol(regex[0])
        
        parens = 0
        while j < len(regex):
            if regex[j] == '(':
                parens = parens + 1
            if regex[j] == ')':
                parens = parens - 1
            if regex[j] == '|' and parens == 0:
                return Union(parse_regex(regex[0:j]), parse_regex(regex[j+1:]))
            if regex[j] == '\\':
                j = j + 1
            j = j + 1

        j = i
        while j < len(regex):
            if regex[j] not in "?*+":
                return Concat(parse_regex(regex[0:j]), parse_regex(regex[j:]))
            j = j + 1
        
        if len(regex) == i + 1:
            if regex[i] == '*':
                return Star(parse_regex(regex[:i]))
            if regex[i] == '?':
                return Question(parse_regex(regex[:i]))
            if regex[i] == '+':
                return Plus(parse_regex(regex[:i]))
        
    
    return Symbol(regex[0])

#print(parse_regex("(ab | cd+ | b*)? efg"))
#print(parse_regex("(ab | cd+ | b*)? efg").thompson())
#print()

#print(parse_regex("aa(a|b)*(a|b)"))
#print(parse_regex("aa(a|b)*(a|b)").thompson().subset_construction().accept("aaab"))
