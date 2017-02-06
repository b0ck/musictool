import sys
import time
import json

from PyQt5 import QtCore
from logic.api import API
from settings import Settings


class Server(QtCore.QObject, API):

    def run_server(self):
        while True:

            try:

                squeue = self.call_method('get_next_server_command')
                if squeue:
                    print("call method -> " + squeue.command)
                    self.call_method(method_name=squeue.command, arguments=json.loads(squeue.argument_list))

                time.sleep(Settings.SERVER_WAIT_TIME)

            except Exception as ex:
                print(ex)
                pass


if __name__ == "__main__":
    app = QtCore.QCoreApplication(sys.argv)
    server = Server()
    server.run_server()
    sys.exit(app.exec_())

