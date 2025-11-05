import tkinter
from tkinter import filedialog
from PIL.ImageFile import ImageFile
from PIL import ImageTk, Image
from typing import Callable
import numpy as np
import matplotlib.pyplot as plt

root = tkinter.Tk()
root.title("Image Viewer")

file_path = filedialog.askopenfilename(
    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
)

class Canvas:
    def __init__(self, image_path: str, root: tkinter.Tk):
        self.root = root
        self.root.title("Image Viewer")
        self.image_path = image_path
        img = Image.open(image_path)
        tk_img = ImageTk.PhotoImage(img)
        self.label = tkinter.Label(self.root, image=tk_img)
        self.label.__setattr__('image', tk_img)
        self.label.pack()
        self.gray_mode = 0

        menubar = tkinter.Menu(self.root)
        file_menu = tkinter.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть изображение", command=self.open_image)
        file_menu.add_command(label="Переключить режим", command=self.to_shades_of_gray)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menubar)
        show_histogram(img)

    def apply_grayscale_formula(self, img: ImageFile, formula: Callable[[int, int, int], float]) -> Image.Image:
        gray_img = img.convert("RGB").copy()
        pixels = gray_img.load()
        if not pixels:
            raise ValueError("Failed to load image pixels.")
        width, height = gray_img.size
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                gray = int(formula(r, g, b))
                pixels[x, y] = (gray, gray, gray)
        return gray_img
    
    def grayscale_diff(self, img: ImageFile) -> Image.Image:
        gray_img0 = self.apply_grayscale_formula(img, lambda r, g, b: 0.299 * r + 0.587 * g + 0.114 * b)
        gray_img1 = self.apply_grayscale_formula(img, lambda r, g, b: 0.2126 * r + 0.7152 * g + 0.0722 * b)
        diff_img = Image.new("RGB", img.size)
        pixels0 = gray_img0.load()
        pixels1 = gray_img1.load()
        diff_pixels = diff_img.load()
        width, height = img.size
        if not pixels0 or not pixels1 or not diff_pixels:
            raise ValueError("Failed to load image pixels.")

        for x in range(width):
            for y in range(height):
                gray0 = pixels0[x, y][0]
                gray1 = pixels1[x, y][0]
                diff = abs(gray0 - gray1)
                diff_pixels[x, y] = (diff, diff, diff)
        return diff_img

    def to_shades_of_gray(self):
        if not self.image_path:
            return
        
        img = None
        if self.gray_mode == 0:
            self.gray_mode = 1
            image = Image.open(self.image_path)
            img = self.apply_grayscale_formula(image, lambda r, g, b: 0.299 * r + 0.587 * g + 0.114 * b)
            tk_gray_img = ImageTk.PhotoImage(img)
            self.label.config(image=tk_gray_img)
            self.label.__setattr__('image', tk_gray_img)
        elif self.gray_mode == 1:
            self.gray_mode = 2
            image = Image.open(self.image_path)
            img = self.apply_grayscale_formula(image, lambda r, g, b: 0.2126 * r + 0.7152 * g + 0.0722 * b)
            tk_gray_img = ImageTk.PhotoImage(img)
            self.label.config(image=tk_gray_img)
            self.label.__setattr__('image', tk_gray_img)
        elif self.gray_mode == 2:
            self.gray_mode = 3
            image = Image.open(self.image_path)
            img = self.grayscale_diff(image)
            tk_gray_img = ImageTk.PhotoImage(img)
            self.label.config(image=tk_gray_img)
            self.label.__setattr__('image', tk_gray_img)
        elif self.gray_mode == 3:
            self.gray_mode = 0
            image = Image.open(self.image_path)
            tk_img = ImageTk.PhotoImage(image)
            self.label.config(image=tk_img)
            self.label.__setattr__('image', tk_img)
        
        if img:
            show_histogram(img)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if not file_path:
            return
        self.label.pack_forget()
        self.label.destroy()
        self.image_path = file_path
        img = Image.open(file_path)
        tk_img = ImageTk.PhotoImage(img)
        self.label = tkinter.Label(self.root, image=tk_img)
        self.label.__setattr__('image', tk_img)
        self.label.pack()
        self.gray_mode = 0

def show_histogram(image: Image.Image):
    img = image.convert("RGB")
    r, g, b = img.split()
    r_hist = np.array(r).flatten()
    g_hist = np.array(g).flatten()
    b_hist = np.array(b).flatten()

    plt.figure(figsize=(10, 5))
    plt.hist(r_hist, bins=256, color='red', alpha=0.5, label='Red Channel')
    plt.hist(g_hist, bins=256, color='green', alpha=0.5, label='Green Channel')
    plt.hist(b_hist, bins=256, color='blue', alpha=0.5, label='Blue Channel')
    plt.title('Color Histogram')
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()

if file_path:
    app = Canvas(file_path, root)
    app.root.mainloop()
