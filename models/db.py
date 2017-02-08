from peewee import *
from settings import Settings

db = SqliteDatabase(Settings.DB_FILE_NAME)
metadb = SqliteDatabase(Settings.META_DB_FILE_NAME)


class BaseModel(Model):

    class Meta:
        database = db


class Library(BaseModel):

    name = CharField(max_length=255)
    source_path = TextField()

    class Meta:
        indexes = (
            (('name', 'source_path'), True),
        )


class Source(BaseModel):

    library = ForeignKeyField(Library)
    source_url = TextField()

    class Meta:
        indexes = (
            (('library', 'source_url'), True),
        )


class Playlist(BaseModel):

    name = CharField(max_length=255)
    description = TextField()


class PlaylistFiles(BaseModel):

    source = ForeignKeyField(Source)
    playlist = ForeignKeyField(Playlist)

    class Meta:
        indexes = (
            (('source', 'playlist'), True),
        )


class MetaData(BaseModel):

    source = ForeignKeyField(Source)
    key = CharField(max_length=255)
    value = TextField()

    class Meta:
        database = metadb
        indexes = (
            (('source', 'key'), True),
        )


class ServerQueue(BaseModel):

    command = CharField(max_length=255)
    argument_list = CharField(max_length=255)
    done = BooleanField()


def install_db():
    db.connect()
    db.create_tables([Library, Source, Playlist, PlaylistFiles, ServerQueue])
    metadb.connect()
    metadb.create_tables([MetaData])
