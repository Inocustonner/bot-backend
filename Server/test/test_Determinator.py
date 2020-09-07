from Determinator.Determinator import *
import json
import os.path
import sys
import pytest

this_dir = os.path.dirname(os.path.abspath(__file__))
 
@pytest.mark.dependency(name='adding')
def test_adding():
    with open(os.path.join(this_dir, "determinator_data.json"), 'rb') as f:
        data = json.load(f)
    for a in data:
        add_determinator(a['comment'], a['regex'], a['vars'], a['section'], a['outcome'])

    dets = json.loads(get_determinators())
    assert len(dets) == len(data)
    for a in data:
        comment = a['comment']
        assert comment in dets
        assert a['regex'] in dets[comment]['regex']
        assert a['section'] == dets[comment]['section']
        assert a['outcome'] == dets[comment]['outcome']
        
@pytest.mark.dependency(depends=['adding'])
def test_apply():
    def check(app):
        return not json.loads(apply_determinator(app)).get('error', False)
    app1 = "Тб(1) - для первой команды"
    app2 = "Ф1(3) для команды`"
    fail3 = "Ф3(3) для команды"
    assert check(app1)
    assert check(app2)
    assert not check(fail3)

@pytest.mark.dependency(depends=['adding'])    
def test_serialization():
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.rts.yml')
    rts_prev = rts.copy()
    save_rts(fpath)
    load_rts(fpath)
    assert rts_prev == rts
    os.remove(fpath)