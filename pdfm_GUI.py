# pdfm.py
# To build with PyInstaller:
# pyinstaller --noconfirm --onefile --windowed --add-data "images\\pdfmerger\\pdf.png;images" --icon=images/pdfmerger/icon.ico --name="PDF Merger" pdfm.py

import os
import sys
import fitz  # PyMuPDF
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this at runtime
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Merger")
        self.geometry("700x600")
        self.resizable(False, False)

        self.file_paths = []
        self.page_ranges = []

        icon_path = resource_path("images/pdfmerger/pdf.png")
        self.pdf_icon = ctk.CTkImage(
            light_image=Image.open(icon_path),
            size=(24, 24)
        )

        self.title_label = ctk.CTkLabel(
            self, text="Select PDFs & Reorder", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(pady=10)

        self.file_frame = ctk.CTkScrollableFrame(self, width=660, height=350)
        self.file_frame.pack(pady=10)

        btn_row = ctk.CTkFrame(self)
        btn_row.pack(pady=10)

        ctk.CTkButton(btn_row, text="📂 Select PDFs",
                      command=self.select_pdfs).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_row, text="⬆️ Move Up",
                      command=self.move_up).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_row, text="⬇️ Move Down",
                      command=self.move_down).grid(row=0, column=2, padx=10)

        self.merge_button = ctk.CTkButton(
            self, text="🛠️ Merge PDFs", command=self.merge_pdfs, width=180)
        self.merge_button.pack(pady=15)

        self.selected_index = 0

    def select_pdfs(self):
        files = list(filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")]
        ))
        if files:
            self.file_paths = files
            self.selected_index = 0
            self.update_icon_list()

    def update_icon_list(self):
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        self.page_ranges = []

        for idx, path in enumerate(self.file_paths):
            file_name = os.path.basename(path)

            row = ctk.CTkFrame(self.file_frame)
            row.pack(fill="x", pady=4, padx=5)

            label = ctk.CTkLabel(row, image=self.pdf_icon, text=f"  {file_name}",
                                 compound="left", width=250, anchor="w", font=("Segoe UI", 14))
            label.grid(row=0, column=0, padx=(5, 10))

            from_entry = ctk.CTkEntry(row, width=50, placeholder_text="From")
            from_entry.grid(row=0, column=1, padx=(0, 5))

            to_entry = ctk.CTkEntry(row, width=50, placeholder_text="To")
            to_entry.grid(row=0, column=2, padx=(0, 5))

            preview_btn = ctk.CTkButton(row, text="👁 Preview", width=80,
                                        command=lambda p=path, i=idx: self.preview_pages(p, i))
            preview_btn.grid(row=0, column=3, padx=(10, 5))

            self.page_ranges.append((from_entry, to_entry))

            label.bind("<Button-1>", lambda e, i=idx: self.set_selected(i))

        self.highlight_selected()

    def set_selected(self, index):
        self.selected_index = index
        self.highlight_selected()

    def highlight_selected(self):
        for i, widget in enumerate(self.file_frame.winfo_children()):
            widget.configure(
                fg_color=("gray40" if i == self.selected_index else "transparent"))

    def move_up(self):
        if self.selected_index > 0:
            self.file_paths[self.selected_index - 1], self.file_paths[self.selected_index] = \
                self.file_paths[self.selected_index], self.file_paths[self.selected_index - 1]
            self.page_ranges[self.selected_index - 1], self.page_ranges[self.selected_index] = \
                self.page_ranges[self.selected_index], self.page_ranges[self.selected_index - 1]
            self.selected_index -= 1
            self.update_icon_list()

    def move_down(self):
        if self.selected_index < len(self.file_paths) - 1:
            self.file_paths[self.selected_index + 1], self.file_paths[self.selected_index] = \
                self.file_paths[self.selected_index], self.file_paths[self.selected_index + 1]
            self.page_ranges[self.selected_index + 1], self.page_ranges[self.selected_index] = \
                self.page_ranges[self.selected_index], self.page_ranges[self.selected_index + 1]
            self.selected_index += 1
            self.update_icon_list()

    def merge_pdfs(self):
        if not self.file_paths:
            messagebox.showwarning("No PDFs", "Please select PDF files first.")
            return

        doc = fitz.open()
        for i, file in enumerate(self.file_paths):
            try:
                pdf = fitz.open(file)
                from_entry, to_entry = self.page_ranges[i]
                start = from_entry.get()
                end = to_entry.get()

                if start.isdigit() and end.isdigit():
                    start_page = max(0, int(start) - 1)
                    end_page = min(int(end), len(pdf))
                    doc.insert_pdf(pdf, from_page=start_page,
                                   to_page=end_page - 1)
                else:
                    doc.insert_pdf(pdf)

            except Exception as e:
                messagebox.showerror(
                    "Error", f"❌ Failed to add:\n{file}\n\n{e}")

        output_path = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if output_path:
            try:
                doc.save(output_path)
                doc.close()
                messagebox.showinfo(
                    "Success", "✅ PDF merged and saved successfully!")
            except Exception as e:
                messagebox.showerror(
                    "Save Failed", f"❌ Could not save file:\n\n{e}")
        else:
            doc.close()

    def preview_pages(self, filepath, index):
        preview_win = ctk.CTkToplevel(self)
        preview_win.title("Page Preview")
        preview_win.geometry("600x500")

        from_entry, to_entry = self.page_ranges[index]
        start = from_entry.get()
        end = to_entry.get()

        try:
            doc = fitz.open(filepath)
            start_page = int(start) - 1 if start.isdigit() else 0
            end_page = int(end) if end.isdigit() else len(doc)

            canvas = ctk.CTkScrollableFrame(preview_win, width=580, height=460)
            canvas.pack(padx=10, pady=10)

            for i in range(start_page, min(end_page, len(doc))):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                img = Image.frombytes(
                    "RGB", [pix.width, pix.height], pix.samples)
                img = img.resize((300, int(img.height * 300 / img.width)))
                img_tk = ImageTk.PhotoImage(img)

                img_label = ctk.CTkLabel(canvas, image=img_tk, text="")
                img_label.image = img_tk  # Keep reference
                img_label.pack(pady=5)

            preview_win.focus_set()
            preview_win.grab_set()
            preview_win.wait_window()

        except Exception as e:
            messagebox.showerror(
                "Preview Error", f"Failed to preview PDF:\n{e}")


if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
