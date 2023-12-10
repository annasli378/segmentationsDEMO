import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Segmentation DEMO")

        self.image_path = None
        self.edited_image = None
        self.mask_image = None
        self.mask_image_draw = None #ImageDraw.Draw(self.mask_image)
        self.painting = False
        self.erasing = False
        self.last_x, self.last_y = None, None

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Button to load an image
        self.btn_load_image = ttk.Button(self.root, text="Load Image", command=self.load_image)
        self.btn_load_image.grid(row=0, column=0, pady=10)

        # Canvas to display the loaded image
        self.canvas_image = tk.Canvas(self.root, bg="white", width=400, height=400)
        self.canvas_image.grid(row=1, column=0, padx=10)

        # Buttons for editing
        self.btn_edit = ttk.Button(self.root, text="EDIT", command=self.enable_painting)
        self.btn_edit.grid(row=2, column=0, pady=5)

        self.btn_eraser = ttk.Button(self.root, text="ERASER", command=self.enable_eraser)
        self.btn_eraser.grid(row=3, column=0, pady=5)

        self.btn_use_ai = ttk.Button(self.root, text="USE AI", command=self.use_ai)
        self.btn_use_ai.grid(row=4, column=0, pady=5)

        # Canvas for painting and erasing
        self.canvas_paint = tk.Canvas(self.root, bg="black", width=400, height=400)
        self.canvas_paint.grid(row=1, column=1, padx=10)

        # Button to save mask
        self.btn_save_mask = ttk.Button(self.root, text="Save Mask", command=self.save_mask)
        self.btn_save_mask.grid(row=5, column=0, pady=10)

        # Bind mouse events
        self.canvas_paint.bind("<B1-Motion>", self.paint)
        # self.canvas_paint.bind("<ButtonRelease-1>", self.stop_painting)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        if self.image_path:
            # Load the image and display it
            self.original_image = Image.open(self.image_path)
            self.original_image = self.original_image.resize((400, 400))
            self.edited_image = ImageTk.PhotoImage(self.original_image)
            self.canvas_image.create_image(0, 0, anchor=tk.NW, image=self.edited_image)

            # Create a mask image
            self.mask_image = Image.new("RGB", (400, 400), (0, 0, 0))
            self.mask_image_draw = ImageDraw.Draw(self.mask_image)


    def enable_painting(self):
        self.painting = True
        self.erasing = False
        self.canvas_paint.configure(cursor="pencil")

    def enable_eraser(self):
        self.painting = False
        self.erasing = True
        self.canvas_paint.configure(cursor="circle")

    def paint(self, event):
        if self.painting or self.erasing:
            x, y = event.x, event.y
            brush_size = 5
            color = "white" if self.painting else "black"

            if self.last_x and self.last_y:
                self.canvas_paint.create_line(
                    self.last_x, self.last_y, x, y,
                    width=brush_size, fill=color, capstyle=tk.ROUND, smooth=tk.TRUE
                )

                self.mask_image_draw.line([self.last_x, self.last_y, x, y], fill=color, width=brush_size)
                self.mask_image.save('res/tmp.png')
            #painted_mask = Image.alpha_composite(self.original_image.convert("RGB"), self.mask_image.convert("RGB"))

            self.last_x, self.last_y = x, y
            self.update_displayed_image()

    def update_displayed_image(self):
        if self.mask_image and self.original_image:
            mask = self.mask_image.convert("RGBA")
            # black pixels -> transparent
            pixels_array = np.array(mask)
            black_pixels = (pixels_array[:, :, :3] == [0, 0, 0]).all(axis=2)
            pixels_array[black_pixels, 3] = 0
            # white pixels -> red and semitransparent
            white_pixels = (pixels_array[:, :, :3] == [255, 255, 255]).all(axis=2)
            pixels_array[white_pixels, :3] = [255, 0, 0]
            pixels_array[white_pixels, 3] = 128

            mask_image = Image.fromarray(pixels_array, 'RGBA')

            painted_mask = Image.alpha_composite(self.original_image.convert("RGBA"), mask_image)
            self.edited_image = ImageTk.PhotoImage(painted_mask)
            self.canvas_image.create_image(0, 0, anchor=tk.NW, image=self.edited_image)

    def stop_painting(self, event):
        self.painting = False
        self.erasing = False
        self.last_x, self.last_y = None, None

    def use_ai(self):
        # Placeholder for using AI to modify the image
        pass

    def save_mask(self):
        if self.mask_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

            if file_path:
                self.mask_image.save(file_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.geometry("900x600")
    root.mainloop()