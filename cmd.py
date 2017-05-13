import sys
from logic.api import API


if __name__ == "__main__":
    api = API()
    method_name = sys.argv[1:][0]
    arguments = sys.argv[2:]
    api.call_method(called_object=api, method_name=method_name, arguments=arguments)