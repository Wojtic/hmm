import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango
import mysql.connector


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

        self.refcon_on_refresh = False

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)
        self.button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.con_button = Gtk.Button(label="Connection settings")
        self.con_button.connect("clicked", self.show_connection_dialog)
        self.button_box.pack_start(self.con_button, True, True, 0)

        self.recon_button = Gtk.CheckButton(
            label="Refresh whole connection (may not work if disabled)")
        self.recon_button.connect("toggled", self.swap_refcon)
        self.button_box.pack_start(self.recon_button, True, True, 0)

        self.re_button = Gtk.Button(label="Refresh")
        self.re_button.connect("clicked", self.refresh_data)
        self.button_box.pack_start(self.re_button, True, True, 0)

        self.tables_label = Gtk.Label()

        self.box.pack_start(self.button_box, True, True, 0)
        self.box.pack_start(self.tables_label, True, True, 0)

    def swap_refcon(self, widget=None):
        self.refcon_on_refresh = not self.refcon_on_refresh

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(**self.connection_data)
            self.cursor = self.connection.cursor()
            # self.get_tables()
            return self.cursor
        except mysql.connector.Error as err:
            print(err)
            self.show_error_dialog(self, err.msg)
            return None

    def refresh_data(self, widget=None):
        print("Refcon on refresh: " + str(self.refcon_on_refresh))
        if self.cursor is None:
            return
        if self.refcon_on_refresh:
            print("Refreshing connection")
            self.connect_to_database()
        return self.get_tables()

    def get_tables(self, widget=None):
        self.cursor.execute("SHOW TABLES")
        self.tables = [x[0] for x in self.cursor]
        self.tables_data = [self.get_table_data(x) for x in self.tables]
        self.parsed_tables = [self.parse_table_data(
            x) for x in self.tables_data]
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
        return [columns] + data

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
                table += "\n" + "-" * (sum(column_widths) + columns - 1)
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
