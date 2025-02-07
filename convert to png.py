import os
import glob
import shutil
from pdf2image import convert_from_path

def process_directory(input_dir, output_base, relative_path=""):
    """Process a directory recursively, maintaining folder structure"""
    
    # Ensure poppler is in PATH
    if not os.environ.get('PATH', '').lower().find('poppler') >= 0:
        os.environ['PATH'] += r";C:\Program Files\poppler-24.02.0\Library\bin"
    
    # Process all PDFs in current directory
    for pdf_path in glob.glob(os.path.join(input_dir, "*.pdf")):
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = os.path.join(output_base, relative_path, pdf_name)
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            print(f"Converting: {pdf_path}")
            images = convert_from_path(
                pdf_path,
                300,
                poppler_path=r"C:\Program Files\poppler-24.02.0\Library\bin"
            )
            
            for i, image in enumerate(images):
                output_path = os.path.join(output_dir, f"{i:03d}.png")
                image.save(output_path, "PNG")
                print(f"Saved: {output_path}")
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
    
    # Process all subdirectories
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            new_relative_path = os.path.join(relative_path, item)
            new_output_dir = os.path.join(output_base, new_relative_path)
            os.makedirs(new_output_dir, exist_ok=True)
            process_directory(item_path, output_base, new_relative_path)

def convert_pdfs_to_png(input_dir=r"C:",
                       output_base=r"C:"):
    """Convert PDFs to PNGs recursively while preserving folder structure"""
    try:
        process_directory(input_dir, output_base)
        print("\nConversion completed successfully!")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    convert_pdfs_to_png()