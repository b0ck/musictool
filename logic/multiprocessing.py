import threading
from queue import Queue

from settings import Settings


class MultiProcessing(object):

    def __init__(self):

        self.queue = Queue()
        self.thread_list = []
        self.current_method = None

    def worker_scanner(self):
        """

        :return:
        """

        while True:
            item = self.queue.get()
            function = getattr(self, self.current_method, None)
            function(item)
            self.queue.task_done()

    def init_queue(self, method, threads_count=1):
        """

        :param method:
        :param threads_count:
        :return:
        """

        if method:
            self.current_method = method
            for tc in range(threads_count):
                worker = threading.Thread(target=self.worker_scanner)
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

    def run_queued_method(self, method_name, value_list):
        """

        :param method_name:
        :param value_list:
        :return:
        """

        if value_list:
            self.clear_queue()
            self.init_queue(method_name, Settings.MAX_THREADS)
            for value in value_list:
                self.queue.put(value)
            self.run_queue()
            self.clear_queue()

    def run_queue(self):
        """

        :return:
        """
        self.queue.join()