import gi
import pickle
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GLib
import mysql.connector


class Data:
    def __init__(self, connection_data, refcon_on_refresh, data_combo_index):
        self.connection_data = connection_data
        self.refcon_on_refresh = refcon_on_refresh
        self.data_combo_index = data_combo_index


class HMM(Gtk.Window):

    def __init__(self):
        super().__init__(title="HMM")
        self.connection_data = None
        self.connection = None
        self.cursor = None
        self.tables = None
        self.tables_data = None
        self.parsed_tables = None
        self.MAX_COL_WIDTH = 15  # including three dots
        self.ignored_tables = []
        self.data_combo_index = 0

        self.refcon_on_refresh = False
        self.refresh_id = None

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(box)
        button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6)

        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.show_save_file_dialog)
        file_box.pack_start(save_button, True, True, 0)

        load_button = Gtk.Button(label="Load")
        load_button.connect("clicked", self.show_load_file_dialog)
        file_box.pack_start(load_button, True, True, 0)

        button_box.pack_start(file_box, True, True, 0)

        con_button = Gtk.Button(label="Connection settings")
        con_button.connect("clicked", self.show_connection_dialog)
        button_box.pack_start(con_button, True, True, 0)

        self.recon_button = Gtk.CheckButton(
            label="Refresh whole connection (may not work if disabled)")
        self.recon_button.connect("toggled", self.swap_refcon)
        button_box.pack_start(self.recon_button, True, True, 0)

        re_button = Gtk.Button(label="Refresh")
        re_button.connect("clicked", self.refresh_data)
        button_box.pack_start(re_button, True, True, 0)

        times = [
            "Only button",
            "1 second",
            "5 seconds",
            "10 seconds",
            "15 seconds",
            "30 seconds",
            "60 seconds",
            "120 seconds",
            "600 seconds",
        ]
        self.time_combo = Gtk.ComboBoxText()
        self.time_combo.set_entry_text_column(0)
        self.time_combo.connect("changed", self.on_time_combobox_changed)
        for time in times:
            self.time_combo.append_text(time)
        self.time_combo.set_active(self.data_combo_index)
        button_box.pack_start(self.time_combo, True, True, 0)

        ignored_tables_label = Gtk.Label(
            label="Ignored tables (comma separated, press enter):")
        ignored_tables_label.set_justify(Gtk.Justification.LEFT)
        button_box.pack_start(ignored_tables_label, True, True, 0)

        ignored_tables_entry = Gtk.Entry()
        ignored_tables_entry.connect("activate", self.set_ignored_tables)
        button_box.pack_start(ignored_tables_entry, True, True, 0)

        self.tables_label = Gtk.Label()

        box.pack_start(button_box, True, True, 0)
        box.pack_start(self.tables_label, True, True, 0)

    def set_ignored_tables(self, widget=None):
        self.ignored_tables = widget.get_text().replace(" ", "").split(",")

    def on_time_combobox_changed(self, combo):
        time = combo.get_active_text()
        self.data_combo_index = combo.get_active()
        if self.refresh_id is not None:
            GLib.source_remove(self.refresh_id)
        if time == "Only button":
            self.refresh_id = None
        else:
            self.refresh_id = GLib.timeout_add(
                int(time.split(" ")[0]) * 1000, self.refresh_data)

    def swap_refcon(self, widget=None):
        self.refcon_on_refresh = not self.refcon_on_refresh

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(**self.connection_data)
            self.cursor = self.connection.cursor()
            return self.cursor
        except mysql.connector.Error as err:
            print(err)
            self.show_error_dialog(self, err.msg)
            return None

    def refresh_data(self, widget=None):
        if self.cursor is None:
            return
        if self.refcon_on_refresh:
            self.connect_to_database()
        self.get_tables()
        return True

    def get_tables(self, widget=None):
        self.cursor.execute("SHOW TABLES")
        self.tables = [x[0] for x in self.cursor]
        self.tables = [x for x in self.tables if x not in self.ignored_tables]
        self.tables_data = [self.get_table_data(x) for x in self.tables]
        self.parsed_tables = ["<b>" + x[1] + "</b>\n" + self.parse_table_data(
            x[0]) for x in self.tables_data]
        self.tables_label.set_markup(
            "<span face='monospace' >" + "\n".join(self.parsed_tables) + "</span>")
        return self.parsed_tables

    def get_table_data(self, table):
        self.cursor.execute("DESCRIBE " + table)
        columns = self.cursor.fetchall()
        '''primary_key = None ------------------- currently asuming primary key is the first column
        for x in columns:
            if 'PRI' in x:
                primary_key = x[0]
                break'''
        columns = [x[0] for x in columns]
        self.cursor.execute("SELECT * FROM " + table)
        data = self.cursor.fetchall()
        # data = data.insert(0, [columns]) -------------------- Nemám tušení proč to nefunguje
        return [columns] + data, table

    def parse_table_data(self, table_data):
        columns = len(table_data[0])
        column_widths = [0] * columns
        for i in range(len(table_data)):
            for j in range(columns):
                if column_widths[j] < len(str(table_data[i][j])):
                    column_widths[j] = len(str(table_data[i][j]))
        for i in range(columns):
            if column_widths[i] > self.MAX_COL_WIDTH:
                column_widths[i] = self.MAX_COL_WIDTH
        table = ""
        for row in range(len(table_data)):
            for column in range(columns):
                text = str(table_data[row][column])
                if len(text) > self.MAX_COL_WIDTH:
                    text = text[:self.MAX_COL_WIDTH - 3] + "..."
                table += text.ljust(column_widths[column]) + "|"
            table = table[:-1]
            if row == 0:
                table += "\n"
                for i in column_widths:
                    table += "-" * i + "+"
                table = table[:-1]
            table += "\n"
        return table

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

    def show_save_file_dialog(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(dialog.get_filename() + ".pkl", "wb") as outp:
                data = Data(self.connection_data,
                            self.refcon_on_refresh, self.data_combo_index)
                pickle.dump(data, outp,
                            pickle.HIGHEST_PROTOCOL)
        dialog.destroy()

    def show_load_file_dialog(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a pkl file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        filter_ptk = Gtk.FileFilter()
        filter_ptk.set_name("pkl files")
        filter_ptk.add_pattern("*.pkl")
        dialog.add_filter(filter_ptk)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(dialog.get_filename(), "rb") as inpt:
                data = pickle.load(inpt)
                self.connection_data = data.connection_data
                self.refcon_on_refresh = data.refcon_on_refresh
                self.data_combo_index = data.data_combo_index
                self.connect_to_database()
                self.recon_button.set_active(self.refcon_on_refresh)
                self.time_combo.set_active(self.data_combo_index)

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
