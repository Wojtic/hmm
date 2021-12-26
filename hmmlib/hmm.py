import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class HMM(Gtk.Window):
    def __init__(self):
        super().__init__(title="HMM")
        self.button = Gtk.Button(label="Connection settings")
        self.button.connect("clicked", self.show_connection_dialog)
        self.add(self.button)

    def show_connection_dialog(self, widget):
        dialog = Gtk.Dialog(title="Connect to server",
                            parent=self,
                            flags=Gtk.DialogFlags.MODAL,
                            buttons=["Connect", Gtk.ResponseType.OK])
        dialog.set_default_size(150, 100)

        a_label = Gtk.Label("Server Adress:")
        a_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(a_label, True, True, 0)

        a_entry = Gtk.Entry()
        a_entry.set_text("localhost")
        a_entry.set_hexpand(True)
        dialog.vbox.pack_start(a_entry, True, True, 0)

        p_label = Gtk.Label("Server Port:")
        p_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(p_label, True, True, 0)

        p_entry = Gtk.SpinButton.new_with_range(1, 65535, 1)
        p_entry.set_value(3306)
        p_entry.set_hexpand(True)
        dialog.vbox.pack_start(p_entry, True, True, 0)

        un_label = Gtk.Label("Username:")
        un_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(un_label, True, True, 0)

        un_entry = Gtk.Entry()
        un_entry.set_text("root")
        un_entry.set_hexpand(True)
        dialog.vbox.pack_start(un_entry, True, True, 0)

        pw_label = Gtk.Label("Password:")
        pw_label.set_halign(Gtk.Align.START)
        dialog.vbox.pack_start(pw_label, True, True, 0)

        pw_entry = Gtk.Entry()
        pw_entry.set_text("")
        pw_entry.set_hexpand(True)
        dialog.vbox.pack_start(pw_entry, True, True, 0)

        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Adress:", a_entry.get_text())
            print("Port:", p_entry.get_value_as_int())
            print("Username:", un_entry.get_text())
            print("Password:", pw_entry.get_text())
        dialog.destroy()


win = HMM()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
