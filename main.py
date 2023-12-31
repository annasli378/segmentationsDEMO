import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import models
from logic import ModelPredict
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model

from skimage.io import imsave


class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Segmentation DEMO")

        # vars
        self.image_path = None
        self.edited_image = None
        self.mask_image = None
        self.mask_image_draw = None
        self.painting = False
        self.erasing = False
        self.last_x, self.last_y = None, None

        # load mode here so it is in memory:
        self.model_path = "models/dcunet_aug1_k2_TF_poprawione_k5.h5"
        self.model = tf.keras.models.load_model(self.model_path)
        self.model.summary()
        self.model.compile()

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Button to load an image
        self.btn_load_image = ttk.Button(self.root, text="Load Image", command=self.load_image)
        self.btn_load_image.grid(row=0, column=0, pady=10)

        # Canvas to display the loaded image
        self.label_image= tk.Label(text="Loaded image")
        self.label_image.grid(row=1, column=0, padx=10)

        self.canvas_image = tk.Canvas(self.root, bg="white", width=512, height=512)
        self.canvas_image.grid(row=2, column=0, padx=10)

        # Buttons for editing mask
        self.btn_frame = ttk.Frame(self.root, padding=10)
        self.btn_frame.grid(row=0, column=1)

        self.btn_edit = ttk.Button(self.btn_frame, text="EDIT", command=self.enable_painting)
        self.btn_edit.grid(row=0, column=0, pady=5, padx=15)

        self.btn_eraser = ttk.Button(self.btn_frame, text="ERASER", command=self.enable_eraser)
        self.btn_eraser.grid(row=0, column=1, pady=5, padx=15)

        # Canvas for painting and erasing
        self.label_image= tk.Label(text="Paint mask")
        self.label_image.grid(row=1, column=1, padx=10)

        self.canvas_paint = tk.Canvas(self.root, bg="black", width=512, height=512)
        self.canvas_paint.grid(row=2, column=1, padx=10)

        # segment with ai
        self.btn_use_ai = ttk.Button(self.btn_frame, text="USE AI", command=self.use_ai)
        self.btn_use_ai.grid(row=0, column=2, pady=5, padx=15)

        self.label_image= tk.Label(text="Mask generated with AI")
        self.label_image.grid(row=1, column=2, padx=10)

        self.canvas_mask_ai = tk.Canvas(self.root, bg="black", width=512, height=512)
        self.canvas_mask_ai.grid(row=2, column=2, padx=10)


        # Button to save mask
        self.btn_save_mask = ttk.Button(self.root, text="Save Mask", command=self.save_mask)
        self.btn_save_mask.grid(row=3, column=1, pady=10)

        # Bind mouse events
        self.canvas_paint.bind("<B1-Motion>", self.paint)
        self.canvas_paint.bind("<ButtonRelease-1>", self.stop_painting)

        # Configure column and row weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)


    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        if self.image_path:
            # Load the image and display it
            self.original_image = Image.open(self.image_path)
            self.original_image = self.original_image.resize((512, 512))
            self.edited_image = ImageTk.PhotoImage(self.original_image)
            self.canvas_image.create_image(0, 0, anchor=tk.NW, image=self.edited_image)

            # Create a mask image
            self.mask_image = Image.new("RGB", (512, 512), (0, 0, 0))
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



    def update_displayed_image_with_ai(self):
        self.mask_image_ai = Image.open("res/tmp.png")
        self.mask_image_ai = self.mask_image_ai.resize((512, 512))
        self.mask_ai = ImageTk.PhotoImage(self.mask_image_ai)
        self.canvas_mask_ai.create_image(0, 0, anchor=tk.NW, image=self.mask_ai)




    def stop_painting(self, event):

        #self.painting = False
        #self.erasing = False
        self.last_x, self.last_y = None, None

    def use_ai(self):
        org = Image.open(self.image_path)
        size_x = 512
        size_y = 224
        img = np.array(org)
        img.resize(1,size_x,size_y,3)
        print(img.shape)

        thresh = 0.1
        predicted = self.model.predict(img, verbose=1)
        masks = np.zeros((len(predicted), size_x, size_y), dtype=np.uint8)
        ns = predicted[:, :, :, 2]
        masks[ns > thresh] = 255

        for n in masks:
            imsave('res/tmp.png', n)

        self.update_displayed_image_with_ai()


    def save_mask(self):
        if self.mask_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

            if file_path:
                self.mask_image.save(file_path)


if __name__ == "__main__":

    root = tk.Tk()
    app = ImageEditorApp(root)
    root.geometry("1500x700")
    root.mainloop()
