import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_list = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list.extend(page.get_images(full=True))
    
    for image_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_path = os.path.join(output_folder, f"extracted_image_{image_index}.{image_ext}")
        
        with open(image_path, "wb") as img_file:
            img_file.write(image_bytes)
        
        image_list.append(image_path)
    
    return image_list