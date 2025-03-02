from .Regex import Regex, parse_regex
from .NFA import NFA
from functools import reduce
from dataclasses import dataclass

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec
        # keeps the order in the spec for some reason
        self.spec.reverse()

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

        # if an error occurs and the lexing fails, you should return none

        

        # convert regex to nfa
        nfa = []
        for pair in self.spec:
            nfa.append(parse_regex(pair[1]).thompson())

        # remap states for each nfa
        new_state_start = 1

        for i in range(len(nfa)):
            nfa[i] = nfa[i].remap_states(lambda state: state - min(nfa[i].K) + new_state_start)
            new_state_start = max(nfa[i].K) + 1
            nfa[i].Tokens = {next(iter(nfa[i].F)): self.spec[i][0]}

        # combine nfa into an unique nfa
        q0 = 0
        S = set()
        K = set({0})
        d = {}
        d[(0, '')] = []
        F = set()
        Tokens = {}
        for aux in nfa:
            S = S | aux.S
            K = K | aux.K
            d = d | aux.d
            d[(0, '')].append(aux.q0)
            F = F | aux.F
            Tokens = Tokens | aux.Tokens

        unique_nfa = NFA(S, K, q0, d, F, Tokens)

        lexer_dfa = unique_nfa.subset_construction()

        i = 0
        j = 1
        accept_aux = 0
        ret_list = []
        line = 0

        # create a list that saves how many characters there were in the text until the idx line
        lines = word.splitlines()
        lines_chars = [0]
        idx = 1
        while idx <= len(lines):
            lines_chars.append(lines_chars[idx - 1] + len(lines[idx - 1]) + 1)
            idx = idx + 1

        while i <= len(word) and j <= len(word):
            aux_word = word[i:j]
            if aux_word[-1] not in lexer_dfa.S:
                return [("", f"No viable alternative at character {j - 1 - lines_chars[line]}, line {line}")]

            ret_val = lexer_dfa.accept(aux_word)
            if ret_val:
                # save the idx for the last accepting word
                accept_aux = j
            
            if j == len(word):
                if accept_aux == 0:
                    if i + 1 == len(word):
                        return [("", f"No viable alternative at character EOF, line {line}")]
                    return [("", f"No viable alternative at character {i + 1 - lines_chars[line]}, line {line}")]
                else:
                    aux_word = word[i:accept_aux]
                    ret_list.append((lexer_dfa.accept(aux_word), aux_word))
                    i = accept_aux
                    j = i
                    accept_aux = 0
                    if '\n' in aux_word:
                        line = line + 1

            j = j + 1


        return ret_list


# spec = [
# 			("SPACE", "\\ "),
# 			("NEWLINE", "\n"),
# 			("ABC", "a(b+)c"),
# 			("AS", "a+"),
# 			("BCS", "(bc)+"),
# 			("DORC", "(d|c)+")
# 		]

# lexer = Lexer(spec)

# print(lexer.lex("\naaa\nbabbcbcbc abbbcaabc"))