import ast
import time

from logic.serverapi import ServerAPI
from settings import Settings


class Server(ServerAPI):

    def run_server(self):
        while True:

            try:

                squeue = self.call_method('get_next_server_command')
                if squeue:
                    print("call method -> ", squeue.command)
                    print("arguments -> ", squeue.argument_list)
                    self.call_method(method_name=squeue.command, arguments=ast.literal_eval(squeue.argument_list))
                    squeue.done = True
                    squeue.save()

                time.sleep(Settings.SERVER_WAIT_TIME)

            except Exception as ex:
                print(ex)
                pass


if __name__ == "__main__":
    server = Server()
    server.run_server()
