import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import io
from ttkbootstrap import Style
from rembg import remove

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer")
        self.root.geometry("800x800")
        self.root.iconphoto(True, ImageTk.PhotoImage(Image.open("images/logo.png")))
        self.style = Style(theme="cyborg")
        self.root.configure(bg=self.style.colors.bg)

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.load_image)
        self.file_menu.add_command(label="Save", command=self.save_image)
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Change Language", command=self.change_language)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        self.toolbar = ttk.Frame(self.root, padding=(5, 2))
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.load_button = ttk.Button(self.toolbar, text="Open", command=self.load_image, style="success.TButton")
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        self.save_button = ttk.Button(self.toolbar, text="Save", command=self.save_image, style="primary.TButton")
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.remove_bg_button = ttk.Button(self.toolbar, text="Remove Background", command=self.remove_background, style="warning.TButton")
        self.remove_bg_button.grid(row=0, column=2, padx=5, pady=5)

        self.compress_button = ttk.Button(self.toolbar, text="Compress", command=self.compress_image, style="secondary.TButton")
        self.compress_button.grid(row=0, column=3, padx=5, pady=5)

        self.quality_button = ttk.Button(self.toolbar, text="Quality", command=self.change_quality, style="info.TButton")
        self.quality_button.grid(row=0, column=4, padx=5, pady=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.images = {}
        self.current_tab = None
        self.compression_quality = 90

        self.translations = {
            'EN': {
                'load_image': "Open",
                'save_image': "Save",
                'remove_background': "Remove Background",
                'compress': "Compress",
                'quality': "Quality",
                'choose_language': "Choose Language",
                'language_error': "Invalid language code",
            },
            'RU': {
                'load_image': "Открыть",
                'save_image': "Сохранить",
                'remove_background': "Удалить фон",
                'compress': "Сжать",
                'quality': "Качество",
                'choose_language': "Выберите язык",
                'language_error': "Неверный код языка",
            }
        }
        self.language = 'EN'
        self.update_labels()

        self.footer = ttk.Frame(self.root, padding=(5, 2))
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)

        try:
            self.logo_image = Image.open("images/logo.png")
            self.logo_image = self.logo_image.resize((50, 50))  # Resize logo if needed
            self.logo_tk = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = tk.Label(self.footer, image=self.logo_tk)
            self.logo_label.pack(side=tk.LEFT, padx=5)
        except FileNotFoundError:
            self.logo_label = tk.Label(self.footer, text="[Logo]")
            self.logo_label.pack(side=tk.LEFT, padx=5)

        self.text_label = tk.Label(self.footer, text="Domi", font=("Arial", 16))
        self.text_label.pack(side=tk.LEFT, padx=5)

    def change_language(self):
        lang_window = tk.Toplevel(self.root)
        lang_window.title("Change Language")

        lang_var = tk.StringVar(value=self.language)
        tk.Label(lang_window, text="Select Language:").pack(pady=10)

        lang_options = ttk.Combobox(lang_window, textvariable=lang_var, values=["EN", "RU"])
        lang_options.pack(pady=10)
        
        def apply_language():
            selected_lang = lang_var.get()
            if selected_lang in self.translations:
                self.language = selected_lang
                self.update_labels()
                lang_window.destroy()
            else:
                messagebox.showerror("Error", self.translations[self.language]['language_error'])

        ttk.Button(lang_window, text="Apply", command=apply_language).pack(pady=10)
        ttk.Button(lang_window, text="Cancel", command=lang_window.destroy).pack(pady=5)

    def show_about(self):
        messagebox.showinfo("About", "Image Resizer App\n\nAuthor: Your Name")

    def update_labels(self):
        self.load_button.config(text=self.translations[self.language]['load_image'])
        self.save_button.config(text=self.translations[self.language]['save_image'])
        self.remove_bg_button.config(text=self.translations[self.language]['remove_background'])
        self.compress_button.config(text=self.translations[self.language]['compress'])
        self.quality_button.config(text=self.translations[self.language]['quality'])

    def load_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        if filepath:
            image = Image.open(filepath)
            tab_id = self.add_tab(filepath, image)
            self.images[tab_id] = {'image': image, 'filepath': filepath}
            self.current_tab = tab_id

    def add_tab(self, title, image):
        tab = ttk.Frame(self.notebook)
        
        tab_content = ttk.Frame(tab)
        tab_content.pack(fill=tk.BOTH, expand=True)

        tab_label = ttk.Label(tab_content, text=title, anchor="w")
        tab_label.pack(side=tk.LEFT, padx=(5, 25), pady=5)

        close_button = ttk.Button(tab_content, text="X", command=lambda: self.close_tab(tab))
        close_button.pack(side=tk.RIGHT)

        self.notebook.add(tab, text=title)
        self.notebook.select(tab)

        img_label = tk.Label(tab)
        img_label.pack(fill=tk.BOTH, expand=True)
        self.display_image(img_label, image)

        return tab

    def close_tab(self, tab):
        tab_id = self.notebook.index(tab)
        self.notebook.forget(tab)
        del self.images[tab_id]
        if self.notebook.tabs():
            self.current_tab = self.notebook.tabs()[0]
            self.update_image_display()

    def save_image(self):
        if self.current_tab is None:
            messagebox.showerror("Error", "No image loaded")
            return

        image_data = self.images[self.current_tab]
        image = image_data['image']
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )

        if filepath:
            try:
                image.save(filepath, quality=self.compression_quality if filepath.lower().endswith('.jpg') else None)
                messagebox.showinfo("Success", f"Image saved as {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")

    def remove_background(self):
        if self.current_tab is None:
            messagebox.showerror("Error", "No image loaded")
            return

        image_data = self.images[self.current_tab]
        image = image_data['image']
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            output = remove(img_byte_arr)
            self.images[self.current_tab]['image'] = Image.open(io.BytesIO(output))
            self.update_image_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove background: {e}")

    def compress_image(self):
        if self.current_tab is None:
            messagebox.showerror("Error", "No image loaded")
            return

        self.compression_quality = simpledialog.askinteger("Compression Quality", "Enter compression quality (1-100):", minvalue=1, maxvalue=100)
        if self.compression_quality is not None:
            messagebox.showinfo("Info", f"Compression quality set to {self.compression_quality}")

    def change_quality(self):
        if self.current_tab is None:
            messagebox.showerror("Error", "No image loaded")
            return

        quality = simpledialog.askinteger("Image Quality", "Enter new quality (1-100):", minvalue=1, maxvalue=100)
        if quality is not None:
            self.compression_quality = quality
            messagebox.showinfo("Info", f"Image quality set to {quality}")

    def update_image_display(self):
        if self.current_tab is not None:
            img_label = self.notebook.nametowidget(self.current_tab).winfo_children()[1]
            self.display_image(img_label, self.images[self.current_tab]['image'])

    def display_image(self, label, image):
        image.thumbnail((self.root.winfo_width(), self.root.winfo_height()))
        img_tk = ImageTk.PhotoImage(image)
        label.config(image=img_tk)
        label.image = img_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()
