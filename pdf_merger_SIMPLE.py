import fitz  # PyMuPDF
import os

import tkinter as tk
from tkinter import filedialog


file_paths = filedialog.askopenfilenames(
    title="Select PDF files", filetypes=[("PDF files", "*.pdf")])


if len(file_paths) != 0:
    # Create a new empty PDF document
    doc = fitz.open()
    
    # Add each PDF to the final file
    for file in file_paths:
        try:
            doc.insert_pdf(fitz.open(file))
        except Exception as e:
            print(f"❌ Failed to add {file}: {e}")

    # Save the output
    output_filepath = filedialog.asksaveasfilename(title="Save As",filetypes=[("PDF files","*.pdf")])
    doc.save(f"{output_filepath}.pdf")




    