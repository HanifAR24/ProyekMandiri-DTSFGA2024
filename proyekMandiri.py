import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import matplotlib.pyplot as plt

class MoCaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MoCa - Money Calculate")
        self.root.geometry("800x600")  # Default window size

        # Configure grid to be responsive
        for i in range(4):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)

        # Database connection
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="moca_db"
        )
        self.cursor = self.conn.cursor()
        
        # GUI Components
        self.create_widgets()
        self.update_treeview()

    def create_widgets(self):
        # Form Input
        self.type_label = ttk.Label(self.root, text="Jenis Transaksi:")
        self.type_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")  # Increased padx from 10 to 20 for more space
        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(self.root, textvariable=self.type_var, values=["Pengeluaran", "Pemasukkan"])
        self.type_dropdown.grid(row=0, column=1, padx=20, pady=10, sticky="ew")  # Increased padx from 10 to 20 for more space

        self.category_label = ttk.Label(self.root, text="Kategori:")
        self.category_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.root, textvariable=self.category_var, values=[
            "Gaji Pegawai", "Maintenance Gedung dan Fasilitas", "Asuransi Pegawai",
            "Biaya Makan Siang", "Biaya Produksi", "Biaya Pemasaran",
            "Biaya Listrik dan Air", "Keuntungan Penjualan", "Dana Investor"
        ])
        self.category_dropdown.grid(row=1, column=1, padx=20, pady=10, sticky="ew")  # Increased padx from 10 to 20 for more space

        self.amount_label = ttk.Label(self.root, text="Jumlah:")
        self.amount_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")  # Increased padx from 10 to 20 for more space

        self.add_button = ttk.Button(self.root, text="Tambah Data", command=self.add_data)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.update_button = ttk.Button(self.root, text="Update Data", command=self.update_data)
        self.update_button.grid(row=3, column=2, padx=10, pady=10, sticky="ew")

        self.delete_button = ttk.Button(self.root, text="Hapus Data", command=self.delete_data)
        self.delete_button.grid(row=3, column=3, padx=10, pady=10, sticky="ew")

        # Treeview
        self.tree = ttk.Treeview(self.root, columns=("ID", "Jenis", "Kategori", "Jumlah"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Jenis", text="Jenis Transaksi")
        self.tree.heading("Kategori", text="Kategori")
        self.tree.heading("Jumlah", text="Jumlah")
        self.tree.grid(row=4, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.tree.bind('<ButtonRelease-1>', self.select_item)

        # Visualization Buttons
        self.pie_button = ttk.Button(self.root, text="Analisis Pengeluaran", command=self.show_pie_chart)
        self.pie_button.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        self.bar_button = ttk.Button(self.root, text="Analisis Keuntungan", command=self.show_bar_chart)
        self.bar_button.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

    def add_data(self):
        jenis = self.type_var.get()
        kategori = self.category_var.get()
        jumlah = self.amount_entry.get()

        if not jenis or not kategori or not jumlah:
            messagebox.showerror("Error", "Semua kolom harus diisi!")
            return

        try:
            jumlah = float(jumlah)
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return

        self.cursor.execute("INSERT INTO transaksi (jenis, kategori, jumlah) VALUES (%s, %s, %s)", (jenis, kategori, jumlah))
        self.conn.commit()
        self.update_treeview()
        self.clear_form()

    def update_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih data yang ingin diupdate!")
            return
        
        jenis = self.type_var.get()
        kategori = self.category_var.get()
        jumlah = self.amount_entry.get()

        if not jenis or not kategori or not jumlah:
            messagebox.showerror("Error", "Semua kolom harus diisi!")
            return

        try:
            jumlah = float(jumlah)
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return

        current_item = self.tree.item(selected_item)
        current_values = current_item['values']
        current_id = current_values[0]

        self.cursor.execute("UPDATE transaksi SET jenis=%s, kategori=%s, jumlah=%s WHERE id=%s", (jenis, kategori, jumlah, current_id))
        self.conn.commit()
        self.update_treeview()
        self.clear_form()

    def delete_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih data yang ingin dihapus!")
            return

        current_item = self.tree.item(selected_item)
        current_values = current_item['values']
        current_id = current_values[0]

        self.cursor.execute("DELETE FROM transaksi WHERE id=%s", (current_id,))
        self.conn.commit()
        self.update_treeview()
        self.clear_form()

    def update_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("SELECT id, jenis, kategori, jumlah FROM transaksi")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def clear_form(self):
        self.type_var.set("")
        self.category_var.set("")
        self.amount_entry.delete(0, tk.END)

    def select_item(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        current_item = self.tree.item(selected_item)
        values = current_item['values']

        self.type_var.set(values[1])
        self.category_var.set(values[2])
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, values[3])

    def show_pie_chart(self):
        self.cursor.execute("SELECT kategori, SUM(jumlah) FROM transaksi WHERE jenis='Pengeluaran' GROUP BY kategori")
        data = self.cursor.fetchall()

        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]

        plt.figure(figsize=(10, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Proporsi Pengeluaran')
        plt.axis('equal')
        plt.show()

    def show_bar_chart(self):
        self.cursor.execute("SELECT jenis, SUM(jumlah) FROM transaksi GROUP BY jenis")
        data = self.cursor.fetchall()

        jenis = [row[0] for row in data]
        jumlah = [row[1] for row in data]

        plt.figure(figsize=(10, 6))
        plt.bar(jenis, jumlah, color=['red', 'green'])
        plt.xlabel('Jenis Transaksi')
        plt.ylabel('Jumlah')
        plt.title('Perbandingan Pemasukkan dan Pengeluaran')
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = MoCaApp(root)
    root.mainloop()