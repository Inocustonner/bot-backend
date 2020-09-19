from RegexTemplater.RT import RT
import ruamel.yaml

import sys
import os
from pprint import PrettyPrinter

pp = PrettyPrinter(4)
yaml = ruamel.yaml.YAML()
yaml.register_class(RT)

def main(rts_path):
    if os.path.exists(rts_path):
        with open(rts_path, 'rb') as fstream:
            rts = yaml.load(fstream)
        for comment, body in rts.items():
            if 'section' in body:
                body['SOPairs'] = [(body['section'], body['outcome'])]
                del body['section']
                del body['outcome']
            pp.pprint({comment: body})
        with open(rts_path + '.ed', 'wb') as fstream:
            yaml.dump(rts, fstream)
    else:
        raise Exception("Invalid path to rts")

if __name__ == "__main__":
    main(sys.argv[1])
