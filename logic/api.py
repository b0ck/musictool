import json
import os
import taglib

from logic.modelapi import ModelAPI
from logic.multiprocessing import MultiProcessing
from settings import Settings


class API(MultiProcessing, ModelAPI):

    @staticmethod
    def _get_file_tags(file_path):
        """

        :param file_path:
        :return:
        """

        tags_string = str(taglib.File(file_path).tags)
        if tags_string:
            if '{' in tags_string:
                if not tags_string.startswith('{'):
                    pos = tags_string.find('{')
                    tags_string = tags_string[pos:]

        return json.loads(tags_string)

    def _scan_file(self, library, file_path):
        """

        :param library:
        :param file_path:
        :return:
        """

        tags = self._get_file_tags(file_path=file_path)
        self._add_file_to_library(file_path=file_path, library=library, tags=tags)

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
                                self.queue.put(file_path)
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
        self.clear_queue()
        self.init_queue('_scan_file', Settings.MAX_THREADS, [lib])
        self._scan_folder(root_folder_path=path)
        self.run_queue()
        self.clear_queue()

    def call_method(self, method_name, arguments=[]):
        """

        :param method_name:
        :param arguments:
        :return:
        """

        function = getattr(self, '_' + method_name, None)
        if function:
            return function(*arguments)
