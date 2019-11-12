import os
import gi
import common
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
from tools import hex_to_rgb, create_pixbuf

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Alacritty(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_title('alacritty.yml')
        self.set_role("toolbox")
        self.set_resizable(False)
        self.set_type_hint(Gtk.WindowType.TOPLEVEL)
        self.set_transient_for(common.main_window)
        self.set_position(Gtk.WindowPosition.NONE)
        self.set_keep_above(True)

        vbox0 = Gtk.VBox()
        vbox0.set_spacing(5)
        vbox0.set_border_width(5)
        
        hbox0 = Gtk.HBox()
        hbox0.set_spacing(5)
        hbox0.set_border_width(5)
        
        f = open(common.alacritty_config, "rb")
        self.data = load(f, Loader=Loader)
        output = dump(self.data['colors'], Dumper=Dumper, default_flow_style=False, sort_keys=False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_propagate_natural_width(True)

        self.textview = Gtk.TextView()
        self.textview.set_property("name", "preview")
        self.textview.set_editable(False)

        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(output)
        scrolled_window.add(self.textview)

        hbox0.add(scrolled_window)

        vbox = Gtk.VBox()
        vbox.set_spacing(3)
        vbox.set_border_width(5)

        for key in self.data['colors']:
            label = Gtk.Label()
            label.set_property("name", "dotfiles-header")
            label.set_text(key.upper())
            vbox.add(label)
            for key1 in self.data['colors'][key]:
                hbox = Gtk.HBox()
                label = Gtk.Label()
                label.set_property("name", "dotfiles")
                label.set_text(key1)
                hbox.pack_start(label, True, False, 0)
                label = Gtk.Label()
                label.set_property("name", "dotfiles")
                hex_color = self.data['colors'][key][key1].replace('0x', '#')
                label.set_text(hex_color)
                hbox.pack_start(label, True, False, 0)

                preview_box = ColorPreviewBox(hex_color)
                preview_box.connect('button-press-event', self.on_box_press, label, key, key1)

                hbox.pack_start(preview_box, False, False, 0)

                vbox.pack_start(hbox, False, False, 0)

        hbox0.add(vbox)

        vbox0.add(hbox0)

        hbox = Gtk.HBox()
        hbox.set_spacing(5)
        hbox.set_border_width(5)
        label = Gtk.Label(common.lang['copy_paste_into'].format(common.alacritty_config))
        label.set_property('name', 'dotfiles')
        hbox.add(label)
        button = Gtk.Button.new_with_label(common.lang['close'])
        button.connect_after('clicked', self.close_window)
        hbox.pack_start(button, False, False, 0)
        
        vbox0.pack_start(hbox, False, False, 0)

        self.add(vbox0)
        self.show_all()

    def update_preview(self):
        output = dump(self.data['colors'], Dumper=Dumper, default_flow_style=False, sort_keys=False)
        self.textbuffer.set_text(output)
        
    def on_box_press(self, preview_box, event, label, section, key):
        if common.clipboard_text:
            self.data['colors'][section][key] = common.clipboard_text.replace('#', '0x')
            label.set_text(common.clipboard_text)
            preview_box.update()
            self.update_preview()
            
    def close_window(self, button):
        self.close()


class Xresources(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_title('.Xresources')
        self.set_role("toolbox")
        self.set_resizable(False)
        self.set_type_hint(Gtk.WindowType.TOPLEVEL)
        self.set_transient_for(common.main_window)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_keep_above(True)

        vbox0 = Gtk.VBox()
        vbox0.set_spacing(5)
        vbox0.set_border_width(5)

        hbox0 = Gtk.HBox()
        hbox0.set_spacing(5)
        hbox0.set_border_width(5)

        f = open(common.xresources, "r")
        lines = f.read().splitlines()
        f.close()
        self.data = {}
        for line in lines:
            line = line.strip()
            if line.startswith('*background:') or line.startswith('*foreground:') or line.startswith('*color'):
                key, value = line.split()
                self.data[key] = value

        output = ''
        for key, value in self.data.items():
            output += '{}  {}\n'.format(key, value)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_propagate_natural_width(True)

        self.textview = Gtk.TextView()
        self.textview.set_property("name", "preview")
        self.textview.set_editable(False)

        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(output)
        scrolled_window.add(self.textview)

        hbox0.add(scrolled_window)

        vbox = Gtk.VBox()
        vbox.set_spacing(3)
        vbox.set_border_width(5)

        for key, value in self.data.items():
            hbox = Gtk.HBox()
            label = Gtk.Label()
            label.set_property("name", "dotfiles")
            label.set_text(key[1:])
            hbox.pack_start(label, True, False, 0)
            label = Gtk.Label()
            label.set_property("name", "dotfiles")
            hex_color = self.data[key]
            label.set_text(hex_color)
            hbox.pack_start(label, True, False, 0)

            preview_box = ColorPreviewBox(hex_color)
            preview_box.connect('button-press-event', self.on_box_press, label, key)

            hbox.pack_start(preview_box, False, False, 0)

            vbox.pack_start(hbox, False, False, 0)

        hbox0.add(vbox)

        vbox0.add(hbox0)

        hbox = Gtk.HBox()
        hbox.set_spacing(5)
        hbox.set_border_width(5)
        label = Gtk.Label(common.lang['copy_paste_into'].format(common.xresources))
        label.set_property('name', 'dotfiles')
        hbox.add(label)
        button = Gtk.Button.new_with_label(common.lang['close'])
        button.connect_after('clicked', self.close_window)
        hbox.pack_start(button, False, False, 0)

        vbox0.pack_start(hbox, False, False, 0)

        self.add(vbox0)
        self.show_all()

    def update_preview(self):
        output = ''
        for key, value in self.data.items():
            output += '{}  {}\n'.format(key, value)
        self.textbuffer.set_text(output)

    def on_box_press(self, preview_box, event, label, key):
        if common.clipboard_text:
            self.data[key] = common.clipboard_text
            label.set_text(common.clipboard_text)
            preview_box.update()
            self.update_preview()

    def close_window(self, button):
        self.close()


class ColorPreviewBox(Gtk.EventBox):
    def __init__(self, hex_color):
        super().__init__()
        pixbuf = create_pixbuf((common.settings.clip_prev_size, common.settings.clip_prev_size // 2),
                               hex_to_rgb(hex_color))
        self.gtk_image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.add(self.gtk_image)
        
    def update(self):
        if common.clipboard_text:
            pixbuf = create_pixbuf((common.settings.clip_prev_size, common.settings.clip_prev_size // 2),
                                   hex_to_rgb(common.clipboard_text))
            self.gtk_image.set_from_pixbuf(pixbuf)
