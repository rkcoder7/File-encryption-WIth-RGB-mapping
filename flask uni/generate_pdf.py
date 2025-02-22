from fpdf import FPDF
import os

def generate_pdf(image_paths, output_path="encrypted_images.pdf"):
    pdf = FPDF()
    for image_path in image_paths:
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=180)
    pdf.output(output_path)