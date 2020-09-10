from RegexTemplater.ValueParser import isvalidvar, runParser

from typing import Dict, Optional
from toolz.functoolz import pipe
from ruamel.yaml import YAML, yaml_object
import json
import re
import operator
callOnObject = operator.methodcaller
# RegexTemplater
# Takes initial regex and revars, compiles them
# and exports function to apply regex to a string

class RT:
    yaml_tag = '!RT'
    splitter = '%=%'
    def __init__(self, regex: str, revars: Dict[str, str], replace_spaces_with_optional_spaces = True):
        self.regex = regex
        self.compiled = ""
        if replace_spaces_with_optional_spaces:
            self.regex = r'\s*'.join(self.regex.split())
        self.revars = revars #revars - regex variables
        self.compiled_vars = dict()
        self.__verifyRevars()
        self.__compileRegex()

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            fR'{node.regex}{cls.splitter}{json.dumps(node.revars)}')
    
    @classmethod
    def from_yaml(cls, constructor, node):
        regex, revars_str = node.value.split(cls.splitter, 1)
        return cls(regex, json.loads(revars_str), False)

    def __verifyRevars(self):
        for key in self.revars.keys():
            if not isvalidvar(key):
                raise SyntaxError(
                    f"Variable '{key}' not suffice variable name constraints")
            if self.regex.count(key) > 1:
                raise SyntaxError("Each variable should occure only once")
            elif self.regex.count(key) == 0:
                raise SyntaxError("Each variable should occure at least once")

    def __compileRegex(self):
        piped = pipe(
                self.regex, *[
                    callOnObject('replace', key,
                                 rf'(?P<{key[1:]}>{self.__preparevalue(key[1:], value)})', 1)
                    for key, value in self.revars.items()
                ])
        self.compiled = re.compile(piped)

    def __preparevalue(self, key: str, val: str) -> str:
        pattern, conds = runParser(val)
        self.compiled_vars.update({key: conds})
        return pattern

    def __eval_vars(self, matched_groups: dict) -> Dict[str, str]:
        var_dict = { # apply post-branching
            k: self.compiled_vars[k].get(v, self.compiled_vars[k]['~'](v))
            for k, v in matched_groups.items()
        }
        return dict(map(lambda item: ('$' + item[0], item[1]), var_dict.items()))

    def apply(self, string: str) -> Optional[Dict[str, str]]:
        if (m := self.compiled.fullmatch(string)):
            return self.__eval_vars(m.groupdict())
        else:
            return None


if __name__ == "__main__":
    r=RT(
        "$Тотал \($p\) - для $team команды", {
            '$Тотал': "(Тотал (меньше|больше))",
            '$p': "(\d+)",
            '$team': '(\w+) ? "первой" -> $team1 : $team2'
    })
    print(r.apply("Тотал больше (3) - для первой команды"))
    # https://github.com/vi3k6i5/flashtext
    # for fast replacement