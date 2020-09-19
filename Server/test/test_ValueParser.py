from RegexTemplater.ValueParser import runParser
import pytest
from typing import Tuple

def test_value_parser():
    def comp_values(rp_ret, group: str, is_val_input: str = False, **kwargs) -> Tuple[bool, str]:
        g, conds, input_val = rp_ret
        print(g, conds, input_val)
        if g != group:
            return False, f"Groups did not matched. Expected {group} given {g}"
        if input_val != is_val_input:
            return False, f"Is unput values didn't match. Expected {is_val_input} given {input_val}"
        for key, value in kwargs.items():
            if conds[key] != value:
                return False, f"Conditional[{key}] = {conds[key]},\nbut expected to be \nConditional[{key}] = {value}"
        return True
    assert comp_values(runParser(r"(\w)"), r"\w")
    assert comp_values(runParser(r"((\w))"), r"(\w)")
    assert comp_values(runParser(r"(My name)"), r"My name")
    assert comp_values(runParser(r'(\d) ? "k1" -> "2": "3"'), r"\d", k1="2")
    assert comp_values(runParser(r'(\d) ? "k1" -> "2": ? "k2" -> "3": ? "k3" -> "4": "5"'), r"\d", k1="2", k2="3", k3="4")
    assert comp_values(runParser(r'$team ? "T1" -> $team1: $team2'), "$team", True, T1="$team1")
    
