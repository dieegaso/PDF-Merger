# pdfm_GUI.py

import os
import sys
import fitz  # PyMuPDF
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Merger")
        self.geometry("750x600")
        self.resizable(False, False)

        self.file_paths = []
        self.page_ranges = []
        self.page_counts = []
        self.selected_index = 0

        icon_path = resource_path("images/pdfmerger/pdf.png")
        self.pdf_icon = ctk.CTkImage(
            light_image=Image.open(icon_path),
            size=(24, 24)
        )

        ctk.CTkLabel(
            self, text="Select PDFs & Reorder",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)

        self.file_frame = ctk.CTkScrollableFrame(self, width=700, height=360)
        self.file_frame.pack(pady=10)

        btn_row = ctk.CTkFrame(self)
        btn_row.pack(pady=20, padx=20)

        ctk.CTkButton(btn_row, text="📂 Select PDFs",
                      command=self.select_pdfs).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_row, text="⬆️ Move Up",
                      command=self.move_up).grid(row=0, column=1, padx=8)
        ctk.CTkButton(btn_row, text="⬇️ Move Down",
                      command=self.move_down).grid(row=0, column=2, padx=8)
        ctk.CTkButton(btn_row, text="🗑 Remove",
                      command=self.remove_pdf).grid(row=0, column=3, padx=8)

        self.merge_button = ctk.CTkButton(
            self, text="🛠️ Merge PDFs",
            command=self.merge_pdfs, width=200
        )
        self.merge_button.pack(pady=15)

    # ------------------ FILE HANDLING ------------------

    def select_pdfs(self):
        files = list(filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")]
        ))
        if not files:
            return

        self.file_paths = files
        self.page_counts = []

        for f in files:
            try:
                self.page_counts.append(len(fitz.open(f)))
            except:
                self.page_counts.append(0)

        self.selected_index = 0
        self.update_icon_list()

    def remove_pdf(self):
        if not self.file_paths:
            return

        idx = self.selected_index
        self.file_paths.pop(idx)
        self.page_counts.pop(idx)
        self.page_ranges.pop(idx)

        if self.selected_index >= len(self.file_paths):
            self.selected_index = max(0, len(self.file_paths) - 1)

        self.update_icon_list()

    # ------------------ UI ------------------

    def update_icon_list(self):
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        self.page_ranges = []

        for idx, path in enumerate(self.file_paths):
            row = ctk.CTkFrame(self.file_frame)
            row.pack(fill="x", pady=4, padx=5)

            # FIXED filename truncation
            filename = os.path.basename(path)
            if len(filename) > 30:
                filename = filename[:27] + "..."

            label = ctk.CTkLabel(
                row,
                image=self.pdf_icon,
                text=f"  {filename}",
                compound="left",
                width=240,
                anchor="w",
                font=("Segoe UI", 14)
            )
            label.grid(row=0, column=0, padx=(5, 10))

            pages_lbl = ctk.CTkLabel(
                row,
                text=f"Pages: {self.page_counts[idx]}",
                width=80,
                font=("Segoe UI", 12)
            )
            pages_lbl.grid(row=0, column=1, padx=(0, 10))

            from_entry = ctk.CTkEntry(row, width=50, placeholder_text="1")
            from_entry.grid(row=0, column=2, padx=(0, 5))

            to_entry = ctk.CTkEntry(
                row,
                width=50,
                placeholder_text=str(self.page_counts[idx])
            )
            to_entry.grid(row=0, column=3, padx=(0, 5))

            preview_btn = ctk.CTkButton(
                row,
                text="👁 Preview",
                width=80,
                command=lambda p=path, i=idx: self.preview_pages(p, i)
            )
            preview_btn.grid(row=0, column=4, padx=(10, 5))

            self.page_ranges.append((from_entry, to_entry))
            label.bind("<Button-1>", lambda e, i=idx: self.set_selected(i))

        self.highlight_selected()

    def set_selected(self, index):
        self.selected_index = index
        self.highlight_selected()

    def highlight_selected(self):
        for i, widget in enumerate(self.file_frame.winfo_children()):
            widget.configure(
                fg_color="gray40" if i == self.selected_index else "transparent"
            )

    # ------------------ REORDER ------------------

    def move_up(self):
        i = self.selected_index
        if i > 0:
            for lst in (self.file_paths, self.page_counts, self.page_ranges):
                lst[i - 1], lst[i] = lst[i], lst[i - 1]
            self.selected_index -= 1
            self.update_icon_list()

    def move_down(self):
        i = self.selected_index
        if i < len(self.file_paths) - 1:
            for lst in (self.file_paths, self.page_counts, self.page_ranges):
                lst[i + 1], lst[i] = lst[i], lst[i + 1]
            self.selected_index += 1
            self.update_icon_list()

    # ------------------ MERGE ------------------

    def merge_pdfs(self):
        if not self.file_paths:
            messagebox.showwarning("No PDFs", "Please select PDF files first.")
            return

        doc = fitz.open()

        for i, file in enumerate(self.file_paths):
            try:
                pdf = fitz.open(file)
                start, end = self.page_ranges[i]
                s, e = start.get(), end.get()

                if s.isdigit() and e.isdigit():
                    doc.insert_pdf(
                        pdf,
                        from_page=max(0, int(s) - 1),
                        to_page=min(int(e), len(pdf)) - 1
                    )
                else:
                    doc.insert_pdf(pdf)

            except Exception as ex:
                messagebox.showerror(
                    "Error", f"Failed to add:\n{file}\n\n{ex}")

        output = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if output:
            try:
                doc.save(output)
                messagebox.showinfo("Success", "PDF merged successfully!")
            except Exception as ex:
                messagebox.showerror("Save Failed", str(ex))
        doc.close()

    # ------------------ PREVIEW ------------------

    def preview_pages(self, filepath, index):
        win = ctk.CTkToplevel(self)
        win.title("Page Preview")
        win.geometry("600x500")

        start, end = self.page_ranges[index]
        s = int(start.get()) - 1 if start.get().isdigit() else 0
        e = int(end.get()) if end.get().isdigit() else None

        frame = ctk.CTkScrollableFrame(win, width=580, height=460)
        frame.pack(padx=10, pady=10)

        try:
            doc = fitz.open(filepath)
            for i in range(s, min(e or len(doc), len(doc))):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                img = Image.frombytes(
                    "RGB", [pix.width, pix.height], pix.samples)
                img = img.resize((300, int(img.height * 300 / img.width)))
                tk_img = ImageTk.PhotoImage(img)
                lbl = ctk.CTkLabel(frame, image=tk_img, text="")
                lbl.image = tk_img
                lbl.pack(pady=5)
        except Exception as ex:
            messagebox.showerror("Preview Error", str(ex))


if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
