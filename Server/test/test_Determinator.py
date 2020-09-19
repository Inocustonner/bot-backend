from Determinator.Determinator import *
import pytest
import json
import pprint

with open("test/determinator_data.json", 'rb') as f:
    inp, res = json.load(f)

pp = pprint.PrettyPrinter(4)
pprint = pp.pprint
pformat = pp.pformat

@pytest.mark.dependency()
def test_determinator_add():
    global rts
    for comment, body in inp.items():
        add_determinator(comment, body['regex'], body['dt_vars'], body['SOPairs'])
        assert rts[comment]['regex'] == ensure_fullstring_match(body['regex'])
        assert rts[comment]['SOPairs'] == body['SOPairs']
        assert rts[comment]['rt'].revars == body['dt_vars']

@pytest.mark.dependency(depends=["test_determinator_add"])
def test_determinator_apply():
    def format_pairs(pairs):
        return list(map(lambda pair: [format_out(pair[0]), format_out(pair[1])], map(format_SO, pairs)))
            
    for outcome, ret_pairs in res.items():
        fmtd_pairs = json.dumps(format_pairs(ret_pairs))
        det_ret = apply_determinator(outcome)
        print(fmtd_pairs)
        print(det_ret)
        assert fmtd_pairs == det_ret
