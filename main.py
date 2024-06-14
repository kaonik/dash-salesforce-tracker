import dearpygui.dearpygui as gui
import dearpygui.demo as demo
import pyperclip
import keyboard
import pyautogui as auto
import pywinctl as pwc
from collections import OrderedDict
import logging
from typing import Dict, Any
from record_type import RecordType
import win32gui, win32api, win32con
from time import sleep
import string

logger = logging.getLogger(__name__)


last_clipboard_content = None
dragging_active = move_window = resize_window = False
prefix_list = {"GR-": [], "CN-": [], "Account": []}

salesforce_dict: Dict[str, RecordType] = {}


# region Clipboard
def check_clipboard():
    # TODO: Redo functionality as most captures will be handled by title extract
    global last_clipboard_content
    current_clipboard_content = pyperclip.paste()

    if current_clipboard_content != last_clipboard_content:
        last_clipboard_content = current_clipboard_content

        for prefix, list_reference in prefix_list.items():
            if current_clipboard_content.startswith(prefix):
                list_reference.append(current_clipboard_content)
                gui.configure_item(prefix, items=list_reference)
                break

    # endregion


# region Window Title Extraction
def window_title_extraction():

    window_title = pwc.getActiveWindowTitle()
    parts = window_title.split(" | ", 3)

    if len(parts) == 3 and parts[2].startswith("Salesforce"):
        record, record_type, _ = parts

        if not RecordType.should_ignore(record_type):
            if record_type not in salesforce_dict:
                logger.debug(f"Record type: {record_type} not found. Created.")
                salesforce_dict[record_type] = RecordType(record_type)
                gui.add_listbox(
                    tag=record_type, parent="Main Window", label=record_type
                )

            record_updated = salesforce_dict[record_type].add_value(record)

            if record_updated:
                gui.configure_item(
                    item=record_type,
                    items=list(salesforce_dict[record_type].values.keys()),
                )


# endregion


"""# region Change Viewport
def change_viewport(sender, app_data, user_data):

    def get_new(xy):
        new_x = max(xy[0] + x_delta, 0)
        new_y = max(xy[1] + y_delta, 0)

        return [new_x, new_y]

    global dragging_active, move_window, resize_window
    mouse_x, mouse_y = gui.get_mouse_pos(local=False)

    if user_data == "click":
        # Menu bar check
        if mouse_y <= 20:
            move_window = True

        # Lower right resize check
        elif mouse_x >= (gui.get_viewport_width() - 20) and mouse_y >= (
            gui.get_viewport_height() - 20
        ):
            resize_window = True

        if move_window or resize_window:
            dragging_active = True

    elif dragging_active and user_data == "drag":
        _, x_delta, y_delta = app_data

        if move_window:
            gui.set_viewport_pos(get_new(gui.get_viewport_pos()))

        elif resize_window:
            gui.set_viewport_width(max(mouse_x, 100))
            gui.set_viewport_height(max(mouse_y, 100))

    elif user_data == "release":
        dragging_active = move_window = resize_window = False


# endregion"""


def item_selection(sender, app_data):
    print(gui.get_value(app_data[1]))
    print(gui.get_item_label(app_data[1]))


def toggle_viewport_visibility():
    if dashboard.isVisible:
        dashboard.hide()
    else:
        dashboard.show()


def show_tool(sender, app_data, user_data):
    getattr(gui, user_data)()


tools = [
    "Show About",
    "Show Debug",
    "Show Documentation",
    "Show Font Manager",
    "Show Item Registry",
    "Show Metrics",
    "Show Style Editor",
    "Show Demo",
    "Show Imgui Demo",
    "Show Implot Demo",
]

punctuation_dict = str.maketrans({x: None for x in string.punctuation})

keyboard.add_hotkey("F1", toggle_viewport_visibility, suppress=True)
logging.basicConfig(level=logging.DEBUG)

notepad_shortcut_dict = {"cn": "Case", "co": "Contact"}


def notepad_shortcut_replace(sender, app_data: str, user_data):
    print(sender, app_data, user_data)
    last_words: list = app_data.rsplit(" ", maxsplit=2)
    if len(last_words) > 1:
        check_word: str = last_words[-2]
        # Remove all punctuation
        clean_word = check_word.translate(punctuation_dict)
        word_difference = check_word[len(clean_word) :]
        logger.debug(f"Checking {clean_word} for shortcut match.")

        if clean_word in notepad_shortcut_dict:
            record_type = notepad_shortcut_dict[clean_word]
            logger.debug(f"Checking {record_type} for salesforce_dict match.")

            if record_type in salesforce_dict:

                record_class = salesforce_dict[notepad_shortcut_dict[clean_word]]
                replace = next(iter(record_class.values))
                replace += word_difference
                logger.debug(f"Replacement value: {replace}")

                last_words[-2] = replace

                new_text = " ".join(last_words)
                # readonly necessary to workaround setting value in callback
                # can't set back to false either so mainloop constantly sets to false
                gui.configure_item(item="notepad", readonly=True)
                gui.set_value(item=sender, value=new_text)
                keyboard.send("end")

    print(last_words)


def set_record_limit(sender, app_data, user_data):
    RecordType.record_limit = app_data
    print(RecordType.record_limit)


gui.create_context()


def showdemo():
    demo.show_demo()


with gui.window(tag="Main Window", no_title_bar=True, width=600, height=400):

    with gui.menu_bar():
        with gui.menu(label="File"):
            with gui.menu(label="Settings"):
                gui.add_slider_int(
                    label="Record Limit",
                    default_value=RecordType.record_limit,
                    clamped=True,
                    min_value=5,
                    max_value=50,
                    callback=set_record_limit,
                )

        with gui.menu(label="Tools"):
            # gui.add_menu_item(label="Show Debugger", callback=show_debug, user_data="show_debug")
            for tool in tools:
                if tool == "Show Demo":
                    gui.add_menu_item(label=tool, tag=tool, callback=showdemo)
                else:
                    gui.add_menu_item(
                        label=tool,
                        callback=show_tool,
                        user_data=tool.lower().replace(" ", "_", -1),
                        tag=tool,
                    )

    with gui.collapsing_header(label="Notepad", default_open=True):
        with gui.child_window(tag="notepad_child_window", border=False, height=300):
            gui.add_input_text(
                tag="notepad",
                multiline=True,
                height=200,
                width=-1,
                tab_input=True,
                callback=notepad_shortcut_replace,
            )

    # gui.add_text(tag="text", label="testingthetext", parent="Main Window")
    # gui.set_value("text", "yaimstupid")

    """with gui.handler_registry():
        gui.add_mouse_drag_handler(
            button=0, threshold=0.0, callback=change_viewport, user_data="drag"
        )
        gui.add_mouse_click_handler(callback=change_viewport, user_data="click")
        gui.add_mouse_release_handler(callback=change_viewport, user_data="release")
        gui.add_mouse_double_click_handler(
            callback=change_viewport, user_data="doubleclick"
        )"""

    """with gui.item_handler_registry(tag="item_handler") as handler:
        gui.add_item_clicked_handler(
            callback=item_selection,
        )"""

    # gui.bind_item_handler_registry("text", "item_handler")


TRANSPARENT_COLOR = (255, 0, 255)


def rgb_to_colorref(rgb):
    r, g, b = rgb
    return b << 16 | g << 8 | r


gui.create_viewport(
    title="Dashboard",
    decorated=False,
    always_on_top=True,
    resizable=False,
    clear_color=TRANSPARENT_COLOR,
    x_pos=0,
    y_pos=0,
    width=2560,
    height=1440,
)


gui.setup_dearpygui()
gui.show_viewport()
dashboard = pwc.getWindowsWithTitle(title="Dashboard")[0]
title = "Dashboard"
hwnd = win32gui.FindWindow(None, title)
win32gui.SetWindowLong(
    hwnd,
    win32con.GWL_EXSTYLE,
    win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,
)
win32gui.SetLayeredWindowAttributes(
    hwnd, rgb_to_colorref(TRANSPARENT_COLOR), 255, win32con.LWA_COLORKEY
)
# gui.set_primary_window("Main Window", True)


while gui.is_dearpygui_running():
    if gui.get_frame_count() % 10 == 0:
        check_clipboard()
        window_title_extraction()
        gui.configure_item(
            item="notepad", readonly=False
        )  # bug workaround see notepad_shortcut_replace

    gui.render_dearpygui_frame()

gui.destroy_context()
