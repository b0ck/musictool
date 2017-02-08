from PyQt5.QtWidgets import QApplication
from views.qt.playerview import Player


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    player = Player(sys.argv[1:])
    player.show()

    sys.exit(app.exec_())
