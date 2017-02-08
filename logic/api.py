import os
import taglib

from logic.helpers.multiprocessing import MultiProcessing
from logic.modelapi import ModelAPI
from settings import Settings


class API(ModelAPI):

    file_path_queue = MultiProcessing()
    file_tag_queue = MultiProcessing()

    @staticmethod
    def _get_file_tags(file_path):
        """

        :param file_path:
        :return:
        """

        return taglib.File(file_path).tags

    def _add_file_tags(self, file):
        """

        :param file:
        :return:
        """

        tags = self._get_file_tags(file_path=file.source_url)
        self._add_tags_to_file(file_id=file.get_id(), tags=tags)

    def _scan_file(self, library_id, file_path):
        """

        :param library_id:
        :param file_path:
        :return:
        """

        file = self._add_file_to_library(file_path=file_path, library_id=library_id)
        self.file_tag_queue.queue.put(file)

    def _scan_folder(self, root_folder_path):
        """

        :param root_folder_path:
        :return:
        """
        file_list = []

        for path, subdirs, files in os.walk(root_folder_path):
            for file in files:
                try:

                    file_path = None
                    filename, file_extension = os.path.splitext(file)
                    if file_extension.lower() not in Settings.NOT_USED_ENDINGS:
                        if Settings.DONT_SCAN_HIDDEN_FILES:
                            if not file.startswith('.'):
                                file_path = os.path.join(path, file)
                        else:
                            file_path = os.path.join(path, file)

                        if file_path:
                            if file_path not in file_list:
                                self.file_path_queue.queue.put(file_path)
                                file_list.append(file_path)

                except Exception as ex:
                    pass

    def _add_library(self, name, path):
        """

        :param name:
        :param path:
        :return:
        """

        lib = self._create_library(name=name, path=path)
        self.file_tag_queue.clear_queue()
        self.file_path_queue.clear_queue()

        self.file_path_queue.init_queue(self, '_scan_file', Settings.MAX_THREADS, [lib.get_id()])
        self._scan_folder(root_folder_path=path)
        self.file_path_queue.run_queue()
        self.file_path_queue.clear_queue()

        self.file_tag_queue.init_queue(self, '_add_file_tags', Settings.MAX_THREADS, [])
        self.file_tag_queue.run_queue()
        self.file_tag_queue.clear_queue()

    def call_method(self, method_name, arguments=[]):
        """

        :param method_name:
        :param arguments:
        :return:
        """

        function = getattr(self, '_' + method_name, None)
        if function:
            return function(*arguments)
