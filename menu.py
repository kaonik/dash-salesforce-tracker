import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import pyqtSignal, QObject
from ahk import AHK
import logging

# Create a separate logger
menu_logger = logging.getLogger("app_logger")
menu_logger.setLevel(logging.DEBUG)

menu_def = [
    [
        "Option 1",
        [
            ["Sub Option 1.1", ["Item 1.1.1", "Item 1.1.2"]],
            ["Sub Option 1.2", ["Item 1.2.1", "Item 1.2.2"]],
        ],
    ],
    ["Option 2", ["Item 2.1", "Item 2.2"]],
    [
        "Other Menu",
        [
            ["Option 3", ["Item 3.1", "Item 3.2"]],
            ["Option 4", ["Item 4.1", "Item 4.2"]],
        ],
    ],
    "Option 5",
]


class PopupMenuHandler(QObject):
    hierarchy_signal = pyqtSignal(list)  # Emit hierarchy
    show_menu_signal = pyqtSignal()  # Trigger menu

    def __init__(self, hierarchy_handler, menu_structure=menu_def):
        super().__init__()
        self.hierarchy = []
        self.menu_structure = menu_structure
        self.show_menu_signal.connect(self.show_popup_menu)
        self.hierarchy_signal.connect(hierarchy_handler)

    def get_hierarchy(self, action: QAction) -> None:
        hierarchy = [action.text()]
        parent = action.parentWidget()
        while parent:
            hierarchy.append(parent.title())
            parent = parent.parentWidget()
        hierarchy.pop()  # Remove the top-level menu
        hierarchy.reverse()  # Reverse for top->down hierarchy
        menu_logger.debug(hierarchy)
        self.hierarchy = hierarchy
        self.hierarchy_signal.emit(self.hierarchy)

    def create_popup_menu(self, menu_structure, parent_menu: QMenu = None) -> QMenu:
        if parent_menu is None:
            parent_menu = QMenu()  # Create the top-level menu without a title

        for item in menu_structure:
            if isinstance(item, list):
                # Create a submenu
                submenu = QMenu(item[0], parent_menu)
                parent_menu.addMenu(submenu)
                self.create_popup_menu(item[1], submenu)
            else:
                # Add a single action
                action = QAction(item, parent_menu)
                action.triggered.connect(
                    lambda checked, a=action: self.get_hierarchy(a)
                )
                parent_menu.addAction(action)

        return parent_menu

    def show_popup_menu(self) -> None:
        main_menu = self.create_popup_menu(self.menu_structure)
        cursor = QCursor.pos()
        main_menu.exec_(cursor)

    def show(self) -> None:
        self.show_menu_signal.emit()


def handle_hierarchy(hierarchy) -> None:
    print(f"Action hierarchy: {' -> '.join(hierarchy)}")


def main() -> None:
    # Create an AHK instance
    ahk = AHK()
    # Create the QApplication
    app = QApplication(sys.argv)

    # Create menu
    menu = PopupMenuHandler(handle_hierarchy)

    ahk.add_hotkey("F1", menu.show)
    ahk.start_hotkeys()

    # Start the QApplication event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
