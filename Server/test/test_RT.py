from RegexTemplater.RT import RT

from typing import Tuple
from pprint import PrettyPrinter
import pytest

pp = PrettyPrinter(4)
pformat = pp.pformat
pprint = pp.pprint


def test_rt():
    def comp_values(vars_ret, vars_expected: dict = {}) -> Tuple[bool, str]:
        print(vars_ret)
        for key, value in vars_expected:
            if not vars_ret.get(key, False):
                return (
                    False,
                    f"Expected key '{key}' is not presented in returned vars. \nReturned vars: \n{pformat(vars_ret)}",
                )
            if vars_ret[key] != value:
                return (
                    False,
                    f"Expected value = '{value}' for key '{key}', but got '{vars_ret[key]}'\n. Returned vars: \n{pformat(vars_ret)}",
                )
        return True

    c1 = RT(r"\($n\)", {"$n": r"(\d+)"})
    assert comp_values(c1.apply("(13)"), {"$n": "13"})
    c2 = RT(r"\($n\)", {"$n": r"(\d+)", "$p": "$n"})
    assert comp_values(c1.apply("(13)"), {"$n": "13", "$p": "13"})
