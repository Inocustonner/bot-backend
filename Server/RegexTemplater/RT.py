try:
    from RegexTemplater.ValueParser import isvalidvar, runParser
except ImportError:
    from ValueParser import isvalidvar, runParser

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

    def __init__(self,
                 regex: str,
                 revars: Dict[str, str],
                 replace_spaces_with_optional_spaces=True):
        self.regex = regex.strip()
        self.compiled = ""
        if replace_spaces_with_optional_spaces:
            self.regex = r'\s*'.join(self.regex.split())

        self.revars = revars  #revars - regex variables
        self.compiled_vars = dict()
        self.compiled_vars_dependend = dict() # for variables that accept other vars as input
        self.__verifyRevars()
        self.__compileRegex()

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(
            cls.yaml_tag,
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
            # elif self.regex.count(key) == 0:
            #     raise SyntaxError("Each variable should occure at least once")

    def __compileRegex(self):
        key_pattern = dict()
        for key, value in self.revars.items():
            r = self.__preparevalue(key[1:], value)
            key_pattern.update(r)
            
        piped = pipe(
            self.regex, *[
                callOnObject(
                    'replace', f'${key}',
                    rf'(?P<{key}>{pattern})',
                    1) for key, pattern in key_pattern.items()
            ])
        self.compiled = re.compile(piped)

    def __preparevalue(self, key: str, val: str) -> Dict[str, str]:
        pattern, conds, is_val_input = runParser(val)
        if not is_val_input:
            self.compiled_vars.update({key: conds})
            return {key: pattern}
        else:
            pair = { f'${key}': conds }
            if pattern not in self.compiled_vars_dependend:
                self.compiled_vars_dependend[pattern] = pair
            else:
                self.compiled_vars_dependend[pattern].update(pair)
            return {}
    
    def __eval_var_conds(self, var_conds, input_: str) -> str:
        return var_conds.get(input_, var_conds['~'](input_))

    def __eval_vars(self, matched_groups: dict) -> Dict[str, str]:
        var_dict = {  # apply post-branching
            k: self.__eval_var_conds(self.compiled_vars[k], v)
            for k, v in matched_groups.items()
        }
        evaled_var_dict = dict(
            map(lambda item: ('$' + item[0], item[1]), var_dict.items()))
        evaled_vars_depended = {}
        for var, depended_vars in self.compiled_vars_dependend.items():
            for var_dep, conds in depended_vars.items():
                evaled_vars_depended.update({var_dep: self.__eval_var_conds(conds, evaled_var_dict[var])})
        evaled_var_dict.update(evaled_vars_depended)
        return evaled_var_dict

    def apply(self, string: str) -> Optional[Dict[str, str]]:
        if (m := self.compiled.fullmatch(string)):
            return self.__eval_vars(m.groupdict())
        else:
            return None


if __name__ == "__main__":
    r = RT("$nomTeam", {"$nomTeam": "(\d+)", "$p": "$nomTeam ? \"13\" -> \"match\": \"12\""})
    print(r.regex)
    print(r.compiled)
    print(r.apply("13"))
    # https://github.com/vi3k6i5/flashtext
    # for fast replacement
