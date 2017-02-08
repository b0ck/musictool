import models.db
from models.db import Library, Source, ServerQueue, Playlist, PlaylistFiles, MetaData, metadb


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

        return PlaylistFiles.create(source=file_id, playlist=playlist_id)

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
    def _add_file_to_library(file_path, library_id):
        """

        :param file_path:
        :param library_id:
        :return:
        """

        return Source.create(source_url=file_path, library=library_id)

    @staticmethod
    def _add_tags_to_file(file_id, tags):
        """

        :param file_id:
        :param tags:
        :return:
        """

        data_insert = []

        for key, value in tags.items():
            data_insert.append({'source': file_id, 'key': key, 'value': value})

        if data_insert:
            with metadb.atomic():
                MetaData.insert_many(data_insert).execute()

    @staticmethod
    def _create_library(name, path):
        """

        :param name:
        :param path:
        :return:
        """

        return Library.create(name=name, source_path=path)