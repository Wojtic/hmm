import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import mysql.connector


class HMM(Gtk.Window):

    def __init__(self):
        super().__init__(title="HMM")
        self.connection_data = None
        self.connection = None
        self.button = Gtk.Button(label="Connection settings")
        self.button.connect("clicked", self.show_connection_dialog)
        self.add(self.button)

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(**self.connection_data)
            return self.connection
        except mysql.connector.Error as err:
            print(err)
            self.show_error_dialog(self, err.msg)
            return None

    def show_error_dialog(self, widget, message):
        dialog = Gtk.Dialog(title="Error",
                            parent=self,
                            modal=True)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(150, 100)
        dialog.get_content_area().add(Gtk.Label(label=message))

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def show_connection_dialog(self, widget):
        dialog = Gtk.Dialog(title="Connect to server",
                            parent=self,
                            modal=True)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                           "Connect", Gtk.ResponseType.OK)
        dialog.set_default_size(150, 100)

        a_label = Gtk.Label(label="Server Adress:")
        a_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(a_label, True, True, 0)

        a_entry = Gtk.Entry()
        a_entry.set_text("localhost")
        a_entry.set_hexpand(True)
        dialog.vbox.pack_start(a_entry, True, True, 0)

        p_label = Gtk.Label(label="Server Port:")
        p_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(p_label, True, True, 0)

        p_entry = Gtk.SpinButton.new_with_range(1, 65535, 1)
        p_entry.set_value(3306)
        p_entry.set_hexpand(True)
        dialog.vbox.pack_start(p_entry, True, True, 0)

        un_label = Gtk.Label(label="Username:")
        un_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(un_label, True, True, 0)

        un_entry = Gtk.Entry()
        un_entry.set_text("root")
        un_entry.set_hexpand(True)
        dialog.vbox.pack_start(un_entry, True, True, 0)

        pw_label = Gtk.Label(label="Password:")
        pw_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(pw_label, True, True, 0)

        pw_entry = Gtk.Entry()
        pw_entry.set_text("")
        pw_entry.set_hexpand(True)
        dialog.vbox.pack_start(pw_entry, True, True, 0)

        db_label = Gtk.Label(label="Database:")
        db_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(db_label, True, True, 0)

        db_entry = Gtk.Entry()
        db_entry.set_text("")
        db_entry.set_hexpand(True)
        dialog.vbox.pack_start(db_entry, True, True, 0)

        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.connection_data = {"host": a_entry.get_text(),
                                    "port": p_entry.get_value_as_int(),
                                    "user": un_entry.get_text(),
                                    "database": db_entry.get_text(),
                                    "password": pw_entry.get_text()}
            self.connect_to_database()
        dialog.destroy()


win = HMM()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
