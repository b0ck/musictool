import threading
from queue import Queue

from settings import Settings


class MultiProcessing(object):

    def __init__(self):

        self.queue = Queue()
        self.thread_list = []
        self.current_method = None

    def worker_scanner(self, argument_list=None):
        """

        :return:
        """

        while True:
            try:
                item = self.queue.get()

                try:
                    function = getattr(self, self.current_method, None)
                    if not argument_list:
                        function(item)

                    else:

                        if not isinstance(argument_list, list):
                            a_list = [argument_list, item]
                            argument_list = a_list
                        else:
                            argument_list[1] = item

                        function(*argument_list)

                except Exception as ex_core:
                    #print(item)
                    #print(ex_core)
                    pass

                self.queue.task_done()

            except Exception as ex:
                print(ex)
                pass

    def init_queue(self, method, threads_count=1, arguments=()):
        """

        :param method:
        :param threads_count:
        :param arguments
        :return:
        """

        if method:
            self.current_method = method
            for tc in range(threads_count):
                worker = threading.Thread(target=self.worker_scanner, args=arguments)
                worker.daemon = True
                worker.start()
                self.thread_list.append(worker)

    def clear_queue(self):
        """

        :return:
        """
        for thread in self.thread_list:
            del thread

        self.thread_list = []
        self.queue = Queue()

    def run_queued_method(self, method_name, value_list, arguments=None):
        """

        # :param method_name:
        # :param value_list:
        :return:
        """

        if value_list:
            self.clear_queue()
            self.init_queue(method_name, Settings.MAX_THREADS, arguments=arguments)
            for value in value_list:
                self.queue.put(value)
            self.run_queue()
            self.clear_queue()

    def run_queue(self):
        """

        :return:
        """
        self.queue.join()