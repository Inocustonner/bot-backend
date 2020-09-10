import requests
import json
import pprint


def add_process():
    type_ = input('Type: ')
    vars_ = {}
    varname = input('Var name: ')
    while varname:
        varval = input(f'{varname} = ')
        vars_[varname] = varval
        varname = input('Var name: ')

    new_type = {
        type_: {
            'vars': vars_,
        }
    }
    new_type[type_]['regex'] = input('Regex: ')
    new_type[type_]['section'] = input('Section: ')
    new_type[type_]['outcome'] = input('Outcome: ')
    return requests.post('http://192.168.6.3/api/determinators/apply',
                         data=json.dumps(new_type)).json()


def get_process():
    return json.loads(requests.get(
        'http://192.168.6.3/api/determinators/get_determinators').text)


def remove_process():
    type_ = input('Type: ')
    if type_:
        return json.dumps(requests.get(
            f'http://192.168.6.3/api/determinators/remove?type={type_}').text,
                          indent=4)
    else:
        return ''


def determine_process():
    outcome = input('Outcome: ')
    if outcome:
        return requests.get(
            f'http://192.168.6.3/api/determinators/determine?outcome={outcome}'
        ).json()
    else:
        return ''


def invalidOption():
    pass


def main():
    options = {
        '1': add_process,
        '2': get_process,
        '3': remove_process,
        '4': determine_process
    }
    pp = pprint.PrettyPrinter(2, compact=True)
    while True:
        option = input(
            f"Options: \n{chr(0xa).join([f'{item[0]} -> {item[1].__name__}' for item in options.items()])}\n0 -> exit\n:"
        )
        if option != '0':
            pp.pprint(options.get(option, invalidOption)())
        else:
            break


if __name__ == "__main__":
    main()