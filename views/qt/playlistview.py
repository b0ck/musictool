from PyQt5.QtCore import QAbstractItemModel, QFileInfo, QModelIndex, Qt


class PlaylistModel(QAbstractItemModel):

    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.m_playlist = None

    def rowCount(self, parent=QModelIndex()):
        """

        :param parent:
        :return:
        """

        return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()):
        """

        :param parent:
        :return:
        """

        return self.ColumnCount if not parent.isValid() else 0

    def index(self, row, column, parent=QModelIndex()):
        """

        :param row:
        :param column:
        :param parent:
        :return:
        """

        return self.createIndex(row, column) if self.m_playlist is not None and not parent.isValid() and row >= 0 and row < self.m_playlist.mediaCount() and column >= 0 and column < self.ColumnCount else QModelIndex()

    def parent(self, child):
        """

        :param child:
        :return:
        """

        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        """

        :param index:
        :param role:
        :return:
        """

        if index.isValid() and role == Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.m_playlist.media(index.row()).canonicalUrl()
                return QFileInfo(location.path()).fileName()

            return self.m_data[index]

        return None

    def playlist(self):
        """

        :return:
        """
        return self.m_playlist

    def _disconnect_default_actions(self):
        """

        :return:
        """

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.disconnect(self.begin_insert_items)
            self.m_playlist.mediaInserted.disconnect(self.end_insert_items)
            self.m_playlist.mediaAboutToBeRemoved.disconnect(self.begin_remove_items)
            self.m_playlist.mediaRemoved.disconnect(self.end_remove_items)
            self.m_playlist.mediaChanged.disconnect(self.change_items)

    def _connect_default_actions(self):
        """

        :return:
        """

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.connect(self.begin_insert_items)
            self.m_playlist.mediaInserted.connect(self.end_insert_items)
            self.m_playlist.mediaAboutToBeRemoved.connect(self.begin_remove_items)
            self.m_playlist.mediaRemoved.connect(self.end_remove_items)
            self.m_playlist.mediaChanged.connect(self.change_items)

    def set_playlist(self, playlist):
        """

        :param playlist:
        :return:
        """

        self._disconnect_default_actions()
        self.beginResetModel()
        self.m_playlist = playlist
        self._connect_default_actions()
        self.endResetModel()

    def begin_insert_items(self, start, end):
        """

        :param start:
        :param end:
        :return:
        """

        self.beginInsertRows(QModelIndex(), start, end)

    def end_insert_items(self):
        """

        :return:
        """

        self.endInsertRows()

    def begin_remove_items(self, start, end):
        """

        :param start:
        :param end:
        :return:
        """

        self.beginRemoveRows(QModelIndex(), start, end)

    def end_remove_items(self):
        """

        :return:
        """

        self.endRemoveRows()

    def change_items(self, start, end):
        """

        :param start:
        :param end:
        :return:
        """

        self.dataChanged.emit(self.index(start, 0), self.index(end, self.ColumnCount))
