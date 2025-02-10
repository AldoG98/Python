import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io

class PDFEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("1200x800")
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create canvas for PDF display
        self.canvas = tk.Canvas(self.main_frame, bg='gray90')
        self.canvas.pack(fill='both', expand=True)
        
        # Add scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.canvas.yview)
        self.v_scrollbar.pack(side='right', fill='y')
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient='horizontal', command=self.canvas.xview)
        self.h_scrollbar.pack(side='bottom', fill='x')
        
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        self.current_pdf = None
        self.current_page = 0
        self.zoom_level = 1.0
        
        # Text editing related variables
        self.edit_mode = False
        self.text_widgets = []

    def create_toolbar(self):
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill='x', pady=5, padx=5)
        
        # Open button
        self.open_btn = ttk.Button(toolbar, text="Open PDF", command=self.open_pdf)
        self.open_btn.pack(side='left', padx=5)
        
        # Navigation buttons
        self.prev_btn = ttk.Button(toolbar, text="Previous", command=self.prev_page)
        self.prev_btn.pack(side='left', padx=5)
        
        self.next_btn = ttk.Button(toolbar, text="Next", command=self.next_page)
        self.next_btn.pack(side='left', padx=5)
        
        # Page indicator
        self.page_label = ttk.Label(toolbar, text="Page: 0/0")
        self.page_label.pack(side='left', padx=5)
        
        # Zoom controls
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side='left', padx=5)
        
        # Edit mode button
        self.edit_btn = ttk.Button(
            toolbar, 
            text="Enable Text Editing", 
            command=self.toggle_edit_mode
        )
        self.edit_btn.pack(side='left', padx=5)
        
        # Save button
        self.save_btn = ttk.Button(
            toolbar,
            text="Save Changes",
            command=self.save_changes
        )
        self.save_btn.pack(side='left', padx=5)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                self.current_pdf = fitz.open(file_path)
                self.current_page = 0
                self.update_page_display()
                self.page_label.config(text=f"Page: 1/{len(self.current_pdf)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {str(e)}")

    def update_page_display(self):
        if self.current_pdf and 0 <= self.current_page < len(self.current_pdf):
            page = self.current_pdf[self.current_page]
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
            
            # Convert PyMuPDF pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert PIL image to PhotoImage
            self.photo = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # If in edit mode, reapply text widgets
            if self.edit_mode:
                self.extract_and_make_editable()

    def prev_page(self):
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
            self.page_label.config(text=f"Page: {self.current_page + 1}/{len(self.current_pdf)}")

    def next_page(self):
        if self.current_pdf and self.current_page < len(self.current_pdf) - 1:
            self.current_page += 1
            self.update_page_display()
            self.page_label.config(text=f"Page: {self.current_page + 1}/{len(self.current_pdf)}")

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.update_page_display()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.update_page_display()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.edit_btn.config(text="Disable Text Editing")
            self.extract_and_make_editable()
        else:
            self.edit_btn.config(text="Enable Text Editing")
            self.clear_text_widgets()

    def extract_and_make_editable(self):
        if not self.current_pdf:
            return
            
        self.clear_text_widgets()
        page = self.current_pdf[self.current_page]
        
        # Extract text blocks with their positions
        text_blocks = page.get_text("dict")["blocks"]
        
        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Create text widget for each text span
                        text = tk.Text(
                            self.canvas,
                            height=1,
                            width=len(span["text"]),
                            wrap=tk.NONE,
                            borderwidth=1
                        )
                        text.insert("1.0", span["text"])
                        
                        # Calculate position
                        x0, y0, x1, y1 = span["bbox"]
                        x = x0 * self.zoom_level
                        y = y0 * self.zoom_level
                        
                        # Place text widget on canvas
                        self.canvas.create_window(
                            x, y,
                            window=text,
                            anchor="nw"
                        )
                        self.text_widgets.append(text)

    def clear_text_widgets(self):
        for widget in self.text_widgets:
            widget.destroy()
        self.text_widgets = []

    def save_changes(self):
        if not self.current_pdf:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if save_path:
            try:
                # Create new PDF with edited text
                output_pdf = fitz.open()
                page = output_pdf.new_page(
                    width=self.current_pdf[self.current_page].rect.width,
                    height=self.current_pdf[self.current_page].rect.height
                )
                
                # Insert edited text
                for widget in self.text_widgets:
                    text = widget.get("1.0", tk.END).strip()
                    coords = self.canvas.coords(self.canvas.find_withtag(widget))
                    x, y = coords[0] / self.zoom_level, coords[1] / self.zoom_level
                    page.insert_text((x, y), text)
                
                output_pdf.save(save_path)
                output_pdf.close()
                messagebox.showinfo("Success", "PDF saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditor(root)
    root.mainloop()