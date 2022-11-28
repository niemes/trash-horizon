from libqtile import hook
import subprocess
import os
from libqtile import bar, layout, widget, hook, qtile
from qtile_extras import widget as extrawidgets
from libqtile.config import Click, Drag, Group, Key, Match, hook, Screen, KeyChord
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.dgroups import simple_key_binder
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras.widget import modify

@hook.subscribe.startup
def dbus_register():
    id = os.environ.get('DESKTOP_AUTOSTART_ID')
    if not id:
        return
    subprocess.Popen(['dbus-send',
                      '--session',
                      '--print-reply',
                      '--dest=org.gnome.SessionManager',
                      '/org/gnome/SessionManager',
                      'org.gnome.SessionManager.RegisterClient',
                      'string:qtile',
                      'string:' + id])


mod = "mod4"
terminal = "alacritty"

# █▄▀ █▀▀ █▄█ █▄▄ █ █▄░█ █▀▄ █▀
# █░█ ██▄ ░█░ █▄█ █ █░▀█ █▄▀ ▄█

def resize(qtile, direction):
    layout = qtile.current_layout
    child = layout.current
    parent = child.parent

    while parent:
        if child in parent.children:
            layout_all = False

            if (direction == "left" and parent.split_horizontal) or (
                direction == "up" and not parent.split_horizontal
            ):
                parent.split_ratio = max(5, parent.split_ratio - layout.grow_amount)
                layout_all = True
            elif (direction == "right" and parent.split_horizontal) or (
                direction == "down" and not parent.split_horizontal
            ):
                parent.split_ratio = min(95, parent.split_ratio + layout.grow_amount)
                layout_all = True

            if layout_all:
                layout.group.layout_all()
                break

        child = parent
        parent = child.parent

@lazy.function
def resize_left(qtile):
    current = qtile.current_layout.name
    layout = qtile.current_layout
    if current == "bsp":
        resize(qtile, "left")
    elif current == "columns":
        layout.cmd_grow_left()
    else:
        lazy.layout.shrink()


@lazy.function
def resize_right(qtile):
    current = qtile.current_layout.name
    layout = qtile.current_layout
    if current == "bsp":
        resize(qtile, "right")
    else:
        layout.cmd_grow_right()
        lazy.layout.grow()


@lazy.function
def resize_up(qtile):
    current = qtile.current_layout.name
    layout = qtile.current_layout
    if current == "bsp":
        resize(qtile, "up")
    elif current == "columns":
        layout.cmd_grow_up()
    else:
        lazy.layout.shrink()


@lazy.function
def resize_down(qtile):
    current = qtile.current_layout.name
    layout = qtile.current_layout
    if current == "bsp":
        resize(qtile, "down")
    elif current == "columns":
        layout.cmd_grow_down()
    else:
        lazy.layout.shrink()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html

    # Gnome Session ;
    Key([mod, 'control'], 'l', lazy.spawn('gnome-screensaver-command -l')),
    Key([mod, 'control'], 'q', lazy.spawn(
        'gnome-session-quit --logout --no-prompt')),
    Key([mod, 'shift', 'control'], 'q', lazy.spawn(
        'gnome-session-quit --power-off')),

    # Switch between windows
    Key([mod, "control"], "Left", lazy.layout.flip_left(),
        desc="flip left to right"),
    Key([mod, "control"], "Right", lazy.layout.flip_right(),
        desc="flip right to left"),

    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "f", lazy.window.toggle_floating()),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes

    Key([mod], "Page_Up", lazy.layout.grow()),
    Key([mod], "Page_Down", lazy.layout.shrink()),
    
    Key([mod, "shift"], "space", lazy.layout.flip()),

    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle E tween different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "c", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    #    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([mod], "r", lazy.spawn("rofi -show combi"),
        desc="Spawn a command using a prompt widget"),


    # CUSTOM
    Key([], "XF86AudioRaiseVolume", lazy.spawn(
        "amixer set 'Master' 2%+"), desc='Volume Up'),
    Key([], "XF86AudioLowerVolume", lazy.spawn(
        "amixer set 'Master' 2%-"), desc='volume down'),
    Key([], "XF86AudioMute", lazy.spawn(
        "amixer -D pulse set Master 1+ toggle"), desc='Volume Mute'),
    Key([], "XF86AudioPlay", lazy.spawn(
        "playerctl play-pause"), desc='playerctl'),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous"), desc='playerctl'),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc='playerctl'),
    Key([], "XF86MonBrightnessUp", lazy.spawn(
        "xrandr --output eDP-1 --brightness 0.40"), desc='brightness UP'),
    Key([], "XF86MonBrightnessDown", lazy.spawn(
        "xrandr --output eDP-1 --brightness 0.40"), desc='brightness Down'),

    # Other stuff
    Key([mod], "h", lazy.spawn("roficlip"), desc='clipboard'),
    Key([mod], "s", lazy.spawn("flameshot gui"), desc='Screenshot'),
        # Resize windows
    Key(
        [mod],"Left", lazy.layout.shrink(),
        # lazy.layout.grow_width(-30),
        desc="Resize window left",
    ),
    Key(
        [mod],"Right",lazy.layout.grow(),
        # lazy.layout.grow_width(30),
        desc="Resize window Right",
    ),
    Key(
        [mod], "Down", lazy.layout.down(), desc="Move focus down in current stack pane"
    ),
    Key([mod], "Up", lazy.layout.up(), desc="Move focus up in current stack pane"),
    Key(
        [mod],
        "Left",
        lazy.layout.left(),
        # lazy.layout.next(),
        desc="Move focus left in current stack pane",
    ),
    Key(
        [mod],
        "Right",
        lazy.layout.right(),
        # lazy.layout.previous(),
        desc="Move focus right in current stack pane",
    ),
]

# █▀▀ █▀█ █▀█ █░█ █▀█ █▀
# █▄█ █▀▄ █▄█ █▄█ █▀▀ ▄█


groups = [Group(f"{i+1}", label="") for i in range(8)]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(
                    i.name),
            ),
        ]
    )


###𝙇𝙖𝙮𝙤𝙪𝙩###

layouts = [
    layout.MonadTall(
        border_focus='#2E303E',
        border_normal='#1F1D2E',
        margin=12,
        border_width=1,
    ),
    layout.MonadWide(
        border_focus='#2E303E',
        border_normal='#1F1D2E',
        margin=12,
        border_width=1,
    ),
    layout.Columns(
        margin=12, border_focus='#6C6F93',
        border_normal='#1F1D2E',
        border_width=0
    ),
    # layout.Matrix(border_focus='#1F1D2E',
    #               border_normal='#1F1D2E',
    #               margin=12,
    #               border_width=0,
    #               ),
    layout.Max(
        border_focus='#2E303E',
        border_normal='#1F1D2E',
        margin=12,
        border_width=0,
    ),
    # layout.Floating(	border_focus='#1F1D2E',
    #     border_normal='#1F1D2E',
    #     margin=12,
    #     border_width=0,
    # ),
    # Try more layouts by unleashing below layouts
    # layout.Stack(num_stacks=2),
    # layout.Bsp(
    #     border_focus='#1F1D2E',
    #     border_normal='#1F1D2E',
    #     margin=12,
    #     border_width=0,
    # ),   

    #  layout.RatioTile(),
    #  layout.Tile(	border_focus='#1F1D2E',
    #     border_normal='#1F1D2E',
    #     margin=12,
    # ),
    #  layout.TreeTab(),
    #  layout.VerticalTile(),
    #  layout.Zoomy(),

]


widget_defaults = dict(
    font="Hack Nerd Font",
    fontsize=14,
    background="#1C1E26",
    foreground="#6C6F93",
    padding=3,
)
# extension_defaults = [widget_defaults]


def open_launcher():
    qtile.cmd_spawn("rofi -show drun")

def open_pavu():
    qtile.cmd_spawn("pavucontrol")

def open_powermenu():
    qtile.cmd_spawn("power")

# █▄▄ ▄▀█ █▀█
# █▄█ █▀█ █▀▄

def myTopbar(tray):
    return bar.Bar([
        widget.Spacer(length=20, background='#1C1E26',),

        widget.Image(
            filename='~/.config/qtile/Assets/launch_Icon.png',
            margin=2,
            background='#1C1E26',
        ),

        widget.Spacer(length=20, background='#1C1E26',),

        widget.GroupBox(
            fontsize=16,
            borderwidth=3,
            highlight_method='block',
            active='#EE64AC',
            block_highlight_text_color="#FAB795",
            highlight_color='#1C1E26',
            inactive='#BD85CB',
            foreground='#1C1E26',
            background='#1C1E26',
            this_current_screen_border='#2E303E',
            this_screen_border='#2E303E',
            other_current_screen_border='#2E303E',
            other_screen_border='#2E303E',
            urgent_border='#2E303E',
            rounded=True,
            disable_drag=True,
        ),

        widget.Spacer(length=17, background='#1C1E26',),

        extrawidgets.CurrentLayoutIcon(
            use_mask=True,
            background='#1C1E26',
            foreground='#E95378',
            padding=3,
            scale=0.5,
        ),

        widget.CurrentLayout(
            background='#1C1E26',
            foreground='#6C6F93',
            font='JetBrains Mono Bold',
        ),

        widget.Spacer(
            length=20,
            background='#1C1E26',
        ),

        extrawidgets.GlobalMenu(
            menu_background='#2E303E',
            menu_foreground='#6C6F93',
            highlight_colour='#FAB795',
            padding=7,
            opacity=0.7,
        ),

        widget.TextBox(
            text='●',
            fontsize=14,
            background='#1C1E26',
            foreground='#6C6F93',
            center_aligned=True,
            padding=0,
            margin_left=15,
            margin_right=15,
        ),

        widget.WindowName(
            background='#1C1E26',
            foreground='#6C6F93',
            format="{name}",
            font='JetBrains Mono Bold',
            empty_group_string='Desktop',
            margin=5
        ),


        widget.Spacer(length=20,background='#1C1E26',),

        widget.Systray(
            background='#1C1E26',
            foreground='#FAB795',
            fontsize=2,
            padding=5,
        ),

        # widget.Backlight(),
        widget.Bluetooth(
            format=' {percent:2.0%}',
            font="JetBrains Mono Bold",
            fontsize=12,
            padding=8,
            background='#232530',
            foreground='#FAB795',
        ),

        widget.Image(
            filename='~/.config/qtile/Assets/black-left-clock.png',
            background='#1C1E26',
            padding=0,
            margin=0
        ),

        extrawidgets.UPowerWidget(
            background='#232530',
            battery_height=10,
            # battery_name	None,
            percentage_critical=0.1,
            percentage_low=0.3,
            battery_width=20,# Size of battery icon
            border_charge_colour='#BD85CB', # Border colour when charging.
            border_colour='#25B0BC', # Border colour when discharging.
            border_critical_colour='#EC6A88',
            # decorations	[]	Decorations for widgets
            fill_charge='#BD85CB', #None	Override fill colour when charging
            fill_critical='#EC6A88',
            fill_low='#FAB795',
            fill_normal='#29D398',
            margin=0,
        ),
        widget.Spacer(length=20,background='#232530',),
        widget.TextBox(
            text='﬙',
            size=2,
            font='JetBrains Mono Bold',
            background='#232530',
            foreground='#FAB795',
            margin=15,
        ),
        widget.Memory(
            format='{MemUsed: .0f}{mm}',
            font="JetBrains Mono Bold",
            fontsize=12,
            padding=8,
            background='#232530',
            foreground='#FAB795',
        ),

        widget.CPU(
            format='{percent:2.0%}',
            font="JetBrains Mono Bold",
            fontsize=12,
            padding=8,
            background='#232530',
            foreground='#FAB795',
        ),

        widget.TextBox(
            text="",
            font="Font Awesome 6 Free Solid",
            fontsize=25,
            padding=0,
            background='#232530',
            foreground='#FAB795',
        ),

        widget.PulseVolume(
            font='JetBrains Mono Bold',
            fontsize=12,
            padding=8,
            background='#232530',
            foreground='#FAB795',
            limit_max_volume="True",
            mouse_callbacks={"Button3": open_pavu},
        ),
        

        widget.Image(
            filename='~/.config/qtile/Assets/black-right-clock.png',
            background='#232530',
        ),

        widget.Clock(
            format='  %I:%M %p',
            background='#1C1E26',
            foreground='#FAB795',
            font="JetBrains Mono Bold",
        ),
        widget.KeyboardLayout(
            foreground='#B877DB',
            font="JetBrains Mono Bold",
            configured_keyboards=['us', 'fr'],
            mouse_callbacks={"Button1": lazy.widget["keyboardlayout"].next_keyboard()},
        ),
        widget.Spacer(length=18,background='#1C1E26',),

        widget.QuickExit(
            default_text='⏻',
            fontsize=16,
            padding=0,
            background='#1C1E26',
            foreground='#EC6A88',
            # mouse_callbacks={"Button1": open_powermenu},
        ),
        widget.Spacer(length=12,background='#1C1E26',),

    ],
        30,
        margin=[6, 6, 6, 6]
    )


screenA = myTopbar(False)
screenB = myTopbar(True)

screens = [

    Screen(
        screenA,
        wallpaper='/home/niemes/Pictures/trashup.gif',
        wallpaper_mode='stretch',
    ),
    Screen(
        screenB,
        # wallpaper='/home/niemes/Pictures/vapor.jpg',
        wallpaper='/home/niemes/Pictures/yetta/yetta_ultra.jpg',
        wallpaper_mode='stretch',
    ),

]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    border_focus='#1F1D2E',
    border_normal='#1F1D2E',
    border_width=0,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)

# some other imports
# stuff


@hook.subscribe.startup_once
def autostart():
    # path to my script, under my user directory
    home = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.call([home])


auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
