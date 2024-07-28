import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import pyqtSignal, QObject
from ahk import AHK
import logging


# Create a separate logger
menu_logger = logging.getLogger("app_logger")
menu_logger.setLevel(logging.DEBUG)


DEFAULT_MENU_DATA = [
    {
        "title": "Option 1",
        "items": [
            {"title": "Sub Option 1.1", "items": ["Item 1.1.1", "Item 1.1.2"]},
            {"title": "Sub Option 1.2", "items": ["Item 1.2.1", "Item 1.2.2"]},
        ],
    },
    {"title": "Option 2", "items": ["Item 2.1", "Item 2.2"]},
    {
        "title": "Other Menu",
        "items": [
            {"title": "Option 3", "items": ["Item 3.1", "Item 3.2"]},
            {"title": "Option 4", "items": ["Item 4.1", "Item 4.2"]},
        ],
    },
    "Item 5",
    "Item 6",
]


class PopupMenuHandler(QObject):
    """
    Handles the creation and display of a popup menu.

    Attributes:
        hierarchy_signal (pyqtSignal): Signal emitted when the hierarchy of the selected action is determined.
        show_menu_signal (pyqtSignal): Signal triggered to show the popup menu.

    Args:
        hierarchy_handler: The handler function for the hierarchy signal.
        menu_structure (list): The structure of the menu in the form of a nested list or dictionary.
                               Defaults to DEFAULT_MENU_DATA.

    """

    hierarchy_signal = pyqtSignal(list)  # Emit hierarchy5
    show_menu_signal = pyqtSignal()  # Trigger menu

    def __init__(self, hierarchy_handler, menu_structure=DEFAULT_MENU_DATA):
        super().__init__()
        self.hierarchy = []
        self.menu_structure = menu_structure
        self.show_menu_signal.connect(self.show_popup_menu)
        self.hierarchy_signal.connect(hierarchy_handler)

    def get_hierarchy(self, action: QAction) -> None:
        """
        Retrieves the hierarchy of the selected action and emits the hierarchy signal.

        Args:
            action (QAction): The selected action.

        """
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
        """
        Recursively creates the popup menu based on the menu structure.

        Args:
            menu_structure (list): The structure of the menu in the form of a nested list or dictionary.
            parent_menu (QMenu, optional): The parent menu to add the items to. Defaults to None.

        Returns:
            QMenu: The created popup menu.

        """
        if parent_menu is None:
            parent_menu = QMenu()  # Create the top-level menu without a title

        for item in menu_structure:
            if isinstance(item, dict):
                # Create a submenu
                submenu = QMenu(item["title"], parent_menu)
                parent_menu.addMenu(submenu)
                self.create_popup_menu(item["items"], submenu)
            else:
                # Add a single action
                action = QAction(item, parent_menu)
                action.triggered.connect(
                    lambda checked, a=action: self.get_hierarchy(a)
                )
                parent_menu.addAction(action)

        return parent_menu

    def show_popup_menu(self) -> None:
        """
        Shows the popup menu at the current cursor position.

        """
        main_menu = self.create_popup_menu(self.menu_structure)
        cursor = QCursor.pos()
        main_menu.exec_(cursor)

    def show(self) -> None:
        """
        Triggers the signal to show the popup menu.

        """
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
