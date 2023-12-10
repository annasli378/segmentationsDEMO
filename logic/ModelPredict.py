import numpy as np
import tensorflow as tf
import os


class ModelPredict():
    def __int__(self):
        self.model_path = "models/CFPNET.h5"
        self.model = tf.keras.models.load_model(self.model_path)
        self.model.summary()
    def get_model_prediction(self, image):

        result = self.model.predict(image, verbose=1)
        thresh = 0.5
        ns = result[:,:,:,2]
        size_x = 512
        size_y = 224
        mask = np.zeros((len(result), size_x, size_y, 3), dtype=np.uint8)
        mask[ns>thresh] = [255, 255, 255]

        return mask


