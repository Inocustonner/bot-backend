from toolz.functoolz import compose
from functools import partial

from typing import Dict, Union, Optional, Tuple
from itertools import takewhile
import operator


def isvalidvar(s: str) -> bool:
    return s[0] == "$" and all(map(lambda c: c.isalnum() or c == "_", s[1:]))


class ValueParser:
    def __init__(self, value: str):
        self.v = value.strip()
        self.p = 0
        self.cchar = self.v[0]

    def skipwh(self):
        while self.cchar.isspace():
            self.advance()

    def advance(self, n=1):
        self.p += n
        self.cchar = self.v[self.p] if self.p < len(self.v) else None

    def match(self, s, throw=True) -> Optional[bool]:
        if s == self.v[self.p : self.p + len(s)]:
            self.advance(len(s))
        elif throw:
            raise SyntaxError(
                f"Unexpected token '{self.v[self.p + 1: self.p + len(s)]}', expected '{s}' in: \"{self.v}\"[{self.p}]"
            )
        else:
            return False
        return True

    def group(self) -> str:
        if self.v.count("(") != self.v.count(")"):
            raise SyntaxError("Unbalanced brackets")
        self.match("(")
        opend = 1
        group = ""
        while opend:
            seq = "".join(
                list(takewhile(lambda c: c not in ["(", ")"], self.v[self.p :]))
            )
            self.advance(len(seq))
            group += seq
            if self.cchar == "(":
                opend += 1
                group += "("
            else:
                opend -= 1
                group += ")"
            self.advance()
        return group[:-1]

    def takewhileNotEq(self, C) -> str:
        mtch = "".join(list(takewhile(lambda c: c != C, self.v[self.p :])))
        self.advance(len(mtch))
        return mtch

    def var(self) -> str:
        self.match("$")
        val = "$" + "".join(
            list(takewhile(lambda c: c != ":" and not c.isspace(), self.v[self.p :]))
        )
        if not isvalidvar(val):
            raise SyntaxError(
                f"Variable '{val}' does not suffice variable name constraints"
            )
        return val

    def value(self) -> str:
        if self.cchar == '"':
            self.match('"')
            val = self.takewhileNotEq('"')
            self.match('"')
        else:
            val = self.var()
            self.advance(
                len(val) - 1
            )  # bcs we have already matched '$', but then we concateted it with val again
        return val

    def match_rule(self) -> str:
        self.match('"')
        mtch = self.takewhileNotEq('"')
        self.match('"')
        return mtch
    
    def conditional(self) -> Dict[str, str]:
        mtch = self.match_rule()
        
        self.skipwh()
        self.match("->")
        self.skipwh()

        return {mtch: self.value()}

    def parse(self) -> Tuple[str, Dict[str, str], bool]:
        try:
            g = self.group()
            input_val = False
        except SyntaxError:
            g = self.value()
            input_val = True
            
        conditional = dict()
        if self.cchar:
            self.skipwh()
            while self.match("?", throw=False):
                self.skipwh()
                conditional.update(self.conditional())
                self.skipwh()
                self.match(":")
                self.skipwh()
            self.otherwise_value = self.value()
            conditional["~"] = lambda x: self.otherwise_value
        else:
            conditional["~"] = lambda x: x
        return g, conditional, input_val


def runParser(val: str):
    return ValueParser(val).parse()


if __name__ == "__main__":
    t1 = r"(\w)"
    t2 = r"((\w))"
    t3 = r"((\w)"  # with error thrown
    t4 = r"(Моё имя  3)"
    t5 = r'(Твоё имя 5) ? "t1" -> "Егор1" : "a2"'
    t6 = r'$team ? "t1" -> $team1: ? "t2" -> $team2 : ? "t3" -> $a3 : $a4'

    print(t1, runParser(t1))
    print(t2, runParser(t2))
    try:
        runParser(t3)
    except Exception as e:
        print(e)
    print(t4, runParser(t4))
    print(t5, runParser(t5))
    print(t6, runParser(t6))
