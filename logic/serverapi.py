from logic.api import API
from models.db import Source
from pygame import mixer

class ServerAPI(API):

    @staticmethod
    def _print_log(message):
        """

        :param message:
        :return:
        """

        print(message)

    def _play_file_id(self, file_id):
        """

        :param file_id:
        :return:
        """

        source = Source.get(Source.id == file_id)
        if source:
            self._print_log('Now playing -> ' + source.source_url)
            mixer.init()
            mixer.Sound(source.source_url).play()

        return mixer

    def call_method(self, method_name, arguments=[]):
        """

        :param method_name:
        :param arguments:
        :return:
        """

        super().call_method(self, method_name, arguments)
