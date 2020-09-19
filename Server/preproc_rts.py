from RegexTemplater.RT import RT
import ruamel.yaml

import sys
import os

yaml = ruamel.yaml.YAML()
yaml.register_class(RT)

def main(rts_path):
    if os.path.exists(rts_path):
        with open(rts_path, 'rb') as fstream:
            rts = yaml.load(fstream)
        for comment, body in rts:
            if 'section' in body:
                body['SOPairs'] = [(body['section'], body['oucome'])]
                body.remove('section')
                body.remove('outcome')
        with open(rts_path + '.ed', 'wb') as fstream:
            yaml.dump(rts, fstream)
    else:
        raise Exception("Invalid path to rts")

if __name__ == "__main__":
    main(sys.argv[1])
