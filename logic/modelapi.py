import models.db
from models.db import Library, Source, ServerQueue, Playlist, PlaylistFiles


class ModelAPI(object):

    @staticmethod
    def _install():
        """

        :return:
        """

        models.db.install_db()

    @staticmethod
    def _add_file_to_playlist(playlist_id, file_id):
        """

        :return:
        """

        return PlaylistFiles.create(file=file_id, playlist=playlist_id)

    @staticmethod
    def _create_playlist(name, description):
        """

        :param name:
        :param description:
        :return:
        """

        return Playlist.create(name=name, description=description)

    @staticmethod
    def _play_file_server(file_id):
        """

        :param file_id:
        :return:
        """

        return ServerQueue.create(command="play_file_id", argument_list=str([file_id]), done=False)

    @staticmethod
    def _get_next_server_command():
        """

        :return:
        """

        return ServerQueue.get(ServerQueue.done == False)

    @staticmethod
    def _add_file_to_library(file_path, library, tags):
        """

        :param file_path:
        :param library:
        :param tags:
        :return:
        """

        tags_string = str(tags)
        if tags_string:
            if '{' in tags_string:
                if not tags_string.startswith('{'):
                    pos = tags_string.find('{')
                    tags_string = tags_string[pos:]

        return Source.create(source_url=file_path, library=library, metadata=tags_string)

    @staticmethod
    def _create_library(name, path):
        """

        :param name:
        :param path:
        :return:
        """

        return Library.create(name=name, source_path=path)