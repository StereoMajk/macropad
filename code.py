import board
import digitalio
import time
import rotaryio
import busio
import displayio
import adafruit_displayio_ssd1306
import terminalio
import usb_hid
from fruity_menu.menu import Menu
from adafruit_display_text import label
from adafruit_debouncer import Debouncer
from adafruit_display_shapes.rect import Rect
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


class Key:
    name = ""
    keycodes = []

    def __init__(self, name, keycodes):
        self.name = name
        self.keycodes = keycodes


class Preset:
    name = ""
    keys = []

    def __init__(self, name, keys):
        self.name = name
        self.keys = keys


presets = []
blenderKeys = []
blenderKeys.append(Key("Frame", [Keycode.KEYPAD_PERIOD]))
blenderKeys.append(Key("Move", [Keycode.G]))
blenderKeys.append(Key("Rot", [Keycode.R]))
blenderKeys.append(Key("Scale", [Keycode.S]))
blenderKeys.append(Key("Dup", [Keycode.SHIFT, Keycode.D]))
blenderKeys.append(Key("Mirr", [Keycode.CONTROL, Keycode.M]))
blenderKeys.append(Key("Extr", [Keycode.E]))
blenderKeys.append(Key("Bevel", [Keycode.CONTROL, Keycode.B]))
blenderKeys.append(Key("Fr-", [Keycode.LEFT_ARROW]))
blenderKeys.append(Key("Play", [Keycode.SPACE]))
blenderKeys.append(Key("Fr+", [Keycode.RIGHT_ARROW]))
presets.append(Preset("Blender", blenderKeys))
fusionKeys = []
fusionKeys.append(Key("OffPl", [Keycode.SHIFT, Keycode.CONTROL, Keycode.H]))
fusionKeys.append(Key("Sket", [Keycode.SHIFT, Keycode.CONTROL, Keycode.D]))
fusionKeys.append(Key("Box", [Keycode.SHIFT, Keycode.CONTROL, Keycode.A]))
fusionKeys.append(Key("Cyl", [Keycode.SHIFT, Keycode.CONTROL, Keycode.G]))
fusionKeys.append(Key("Press", [Keycode.Q]))
fusionKeys.append(Key("Comb", [Keycode.SHIFT, Keycode.CONTROL, Keycode.J]))
fusionKeys.append(Key("Fille", [Keycode.F]))
fusionKeys.append(Key("Insp", [Keycode.I]))
fusionKeys.append(Key("SelW", [Keycode.ONE]))
fusionKeys.append(Key("SelF", [Keycode.TWO]))
fusionKeys.append(Key("SelP", [Keycode.THREE]))
presets.append(Preset("Fusion 360", fusionKeys))

selected_preset = presets[0]

kbd = Keyboard(usb_hid.devices)


def create_buttons(group, button_to_port_mapping, buttons, pins, button_text_areas):
    for idx, x in enumerate(button_to_port_mapping):
        btn = digitalio.DigitalInOut(x)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.UP
        pins.append(btn)
        switch = Debouncer(btn)
        buttons.append(switch)

        text = str(0)
        text_area = label.Label(terminalio.FONT, text=text)
        if idx > 3:
            text_area.x = 2 + (idx-4) * 32
        else:
            text_area.x = 2 + idx * 32
        text_area.y = 7 + 16 + int(idx / 4) * 16
        button_text_areas.append(text_area)
        group.append(text_area)


def create_grid(group, rectangles):
    for y in range(2):
        for x in range(4):
            rect = Rect(x * 32, y * 16 + 16, 32, 16,
                        fill=None, outline=0xFFFFFF)
            rectangles.append(rect)
            group.append(rect)

    bottom_rect1 = Rect(16, 3 * 16, 32, 16, fill=None, outline=0xFFFFFF)
    bottom_rect2 = Rect(16 + 32, 3 * 16, 32, 16, fill=None, outline=0xFFFFFF)
    bottom_rect3 = Rect(16 + 32 + 32, 3 * 16, 32, 16,
                        fill=None, outline=0xFFFFFF)
    group.append(bottom_rect1)
    rectangles.append(bottom_rect1)
    group.append(bottom_rect2)
    rectangles.append(bottom_rect2)
    group.append(bottom_rect3)
    rectangles.append(bottom_rect3)


def create_rotary_text(group, rotary_text_areas):
    text1 = str(1)
    text_area1 = label.Label(terminalio.FONT, text=text1)
    text_area1.x = 2 + 16
    text_area1.y = 7 + 48
    rotary_text_areas.append(text_area1)
    group.append(text_area1)

    text2 = str(2)
    text_area2 = label.Label(terminalio.FONT, text=text2)
    text_area2.x = 2 + 16+32
    text_area2.y = 7 + 48
    rotary_text_areas.append(text_area2)
    group.append(text_area2)

    text3 = str(3)
    text_area3 = label.Label(terminalio.FONT, text=text3)
    text_area3.x = 2 + 16+32+32
    text_area3.y = 7 + 48
    rotary_text_areas.append(text_area3)
    group.append(text_area3)


displayio.release_displays()


i2c = busio.I2C(board.GP13, board.GP12)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

top_encoder_btn = digitalio.DigitalInOut(board.GP18)
top_encoder_btn.direction = digitalio.Direction.INPUT
top_encoder_btn.pull = digitalio.Pull.UP
top_encoder_switch = Debouncer(top_encoder_btn)


bottom_encoder_btn = digitalio.DigitalInOut(board.GP21)
bottom_encoder_btn.direction = digitalio.Direction.INPUT
bottom_encoder_btn.pull = digitalio.Pull.UP
bottom_encoder_switch = Debouncer(bottom_encoder_btn)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
top_encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)
bottom_encoder = rotaryio.IncrementalEncoder(board.GP19, board.GP20)

top_encoder_last_position = None
bottom_encoder_last_position = None

grid_group = displayio.Group()
display.show(grid_group)

text = "- " + selected_preset.name
selected_preset_text_area = label.Label(terminalio.FONT, text=text)
selected_preset_text_area.x = 2
selected_preset_text_area.y = 7
grid_group.append(selected_preset_text_area)

rectangles = []

create_grid(grid_group, rectangles)

button_to_port_mapping = [board.GP3, board.GP4, board.GP26, board.GP27,
                          board.GP0, board.GP1, board.GP2, board.GP28]

buttons = []
pins = []
button_text_areas = []
rotary_text_areas = []
in_menu = False
display_changed = True

create_buttons(grid_group, button_to_port_mapping,
               buttons, pins, button_text_areas)
create_rotary_text(grid_group, rotary_text_areas)

menu = Menu(display, 128, 64, title="Select Preset")


def select_preset(name):
    global in_menu
    global display_changed
    global selected_preset
    for preset in presets:
        if preset.name == name:
            selected_preset = preset
            selected_preset_text_area.text = preset.name
            break
    in_menu = False
    display_changed = True
    print(f"{name}")


for preset in presets:
    menu.add_action_button(preset.name, action=select_preset, args=preset.name)

pressed_btm_keys = None
pressed_btm_idx = -1
while True:
    top_encoder_switch.update()
    bottom_encoder_switch.update()

    if top_encoder_switch.fell:
        if not in_menu:
            in_menu = not in_menu
            display_changed = True
        else:
            menu.click()

    if bottom_encoder_switch.fell:
        kbd.press(*selected_preset.keys[9].keycodes)
    if bottom_encoder_switch.rose:
        kbd.release(*selected_preset.keys[9].keycodes)

    # buttons
    for idx, btn in enumerate(buttons):
        btn.update()
        text_area = button_text_areas[idx]
        if idx < len(selected_preset.keys):
            if text_area.text != selected_preset.keys[idx].name:
                text_area.text = selected_preset.keys[idx].name

        if pins[idx].value:
            if text_area.color != 0xFFFFFF:
                rectangles[idx].fill = None
                text_area.color = 0xFFFFFF
        else:
            if text_area.color != 0x000000:
                rectangles[idx].fill = 0xFFFFFF
                text_area.color = 0x000000
        if btn.fell:
            kbd.press(*selected_preset.keys[idx].keycodes)
        if btn.rose:
            kbd.release(*selected_preset.keys[idx].keycodes)

    # top encoder
    top_encoder_position = top_encoder.position
    if top_encoder_last_position is None or top_encoder_position != top_encoder_last_position:
        if not in_menu and top_encoder_last_position is not None:
            in_menu = True
        if top_encoder_last_position is not None:
            delta = top_encoder_last_position - top_encoder_position
            if in_menu:
                menu.scroll(delta)
                display_changed = True
    top_encoder_last_position = top_encoder_position

    # bottom encoder
    for idx, text_area in enumerate(rotary_text_areas):
        if text_area.text != selected_preset.keys[idx + 8].name:
            text_area.text = selected_preset.keys[idx + 8].name

    if pressed_btm_keys is not None:
        kbd.release(*pressed_btm_keys)
        pressed_btm_keys = None
        if pressed_btm_idx == 0:
            rotary_text_areas[0].color = 0xFFFFFF
            rectangles[8].fill = 0x000000
        elif pressed_btm_idx == 2:
            rotary_text_areas[2].color = 0xFFFFFF
            rectangles[10].fill = 0x00000

    bottom_encoder_position = bottom_encoder.position
    if bottom_encoder_last_position is None or bottom_encoder_position != bottom_encoder_last_position:
        if bottom_encoder_last_position is not None:
            delta = bottom_encoder_last_position - bottom_encoder_position
            if delta > 0:
                kbd.press(*selected_preset.keys[8].keycodes)
                pressed_btm_keys = selected_preset.keys[8].keycodes
                rotary_text_areas[0].color = 0x000000
                rectangles[8].fill = 0xFFFFFF
                pressed_btm_idx = 0
            elif delta < 0:
                kbd.press(*selected_preset.keys[10].keycodes)
                pressed_btm_keys = selected_preset.keys[10].keycodes
                rotary_text_areas[2].color = 0x000000
                rectangles[10].fill = 0xFFFFFF
                pressed_btm_idx = 2
    bottom_encoder_last_position = bottom_encoder_position

    display.auto_refresh = True
    if in_menu:
        if display_changed:
            menu.show_menu()
            display_changed = False
    else:
        if display_changed:
            display.show(grid_group)
            display_changed = False
