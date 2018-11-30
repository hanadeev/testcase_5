#!/srv/anaconda3/bin/python3.7

import socket
import logging
import projectconf as cf

logging.disable(logging.CRITICAL)
# logging.basicConfig(level=logging.DEBUG)


class ClientCarCenter:
    """
    Class for working with a remote database of sold cars.
    Usage:
        s = server.ClientCarCenter()
        s.start()
    """
    def __init__(self, host: str = cf.host, port: int = cf.port):
        self.host = host
        self.port = port
        self._socket = None

    def start(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket:
                self._socket.connect((self.host, self.port))
                hello_msg = """
Choose from the following options:
1. Add information about the sold car
2. Request information by serial number
3. Exit"""
                while True:
                    print(hello_msg)
                    try:
                        choice = int(input())
                        if choice == 1:
                            self._add_car()
                        elif choice == 2:
                            self._get_car()
                        elif choice == 3:
                            self._socket.sendall(cf.encode({'close': '1'}))
                            break

                    except ValueError:
                        pass
                print('Close connection')

        except ConnectionRefusedError:
            print("Server is not available. Try later or contact your administrator")
        except BrokenPipeError:
            print("Broken pipe. Contact your administrator")

    def _add_car(self):
        get_properties_form = {'get': 'properties_form'}
        self._socket.sendall(cf.encode(get_properties_form))

        properties_form = cf.decode(self._socket.recv(cf._max_buffer))

        print('Enter properties')
        filled_form = {'insert': self._fill_form(properties_form)}
        logging.debug('filled_form: {}'.format(filled_form))

        self._socket.sendall(cf.encode(filled_form))

        result = cf.decode(self._socket.recv(cf._max_buffer))
        logging.debug('result added car: {}'.format(filled_form))

        print('{} adding car in the base'.format(result.get('state', 'failed')))

    def _get_car(self):
        print('Enter the serial number of the car')
        get_car = {'get': 'car'}
        get_car.update(self._fill_form({'serialNumber': 'uint64'}))
        self._socket.sendall(cf.encode(get_car))

        car = cf.decode(self._socket.recv(cf._max_buffer))

        def pretty_print(d: dict, intend: str = ''):
            for k, v in d.items():
                if isinstance(v, dict):
                    print('{}{}'.format(intend, k))
                    pretty_print(v, intend + '    ')
                else:
                    print('{}{}: {}'.format(intend, k, v))

        if 'state' in car:
            print('failed getting car from the base')
            return

        print('Information about the car')
        pretty_print(car)

    def _fill_form(self, properties: dict, intend: str = '') -> dict:
        def get_valid_input(prompt: str, type_raw: str):
            min_, max_ = cf._input_limits.get(type_raw, (None, None))
            while True:
                val = input('{}{}: '.format(intend, prompt))
                try:
                    type_ = cf._input_types[type_raw]
                    val = type_(val)
                except ValueError:
                    print("{0} value must be {1}.".format(prompt, type_.__name__))
                    continue
                if max_ is not None and val > max_:
                    print("{0} value must be less than or equal to {1}.".format(prompt, max_))
                elif min_ is not None and val < min_:
                    print("{0} value must be greater than or equal to {1}.".format(prompt, min_))
                elif type_ is str and val == '':
                    print("{0} value must not be empty".format(prompt))
                else:
                    return val

        d = {}
        for k, v in properties.items():
            if isinstance(v, dict):
                print('{}{}'.format(intend, k))
                d[k] = self._fill_form(v, intend + '    ')
            else:
                d[k] = get_valid_input(k, v)
        return d
