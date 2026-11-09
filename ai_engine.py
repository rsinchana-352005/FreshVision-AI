
import os
import numpy as np
import pandas as pd
import tensorflow as tf

from PIL import Image, ImageOps

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MANIFEST_DIR = os.path.join(BASE_DIR, "manifests")

IMAGE_SIZE = (224, 224)

MOBILENET_PATH = os.path.join(
    MODEL_DIR, "mobilenetv2_best.keras"
)

EFFICIENTNET_PATH = os.path.join(
    MODEL_DIR, "efficientnetb0_best.keras"
)

TRAIN_MANIFEST = os.path.join(
    MANIFEST_DIR, "fruitnet_train_windows.csv"
)


# --------------------------------------------------
# LOAD CLASS LABELS
# --------------------------------------------------

train_df = pd.read_csv(TRAIN_MANIFEST)

CLASS_NAMES = sorted(
    train_df["class_name"].unique().tolist()
)

NUM_CLASSES = len(CLASS_NAMES)

print("Classes loaded:", NUM_CLASSES)


# --------------------------------------------------
# LOAD TRAINED MODELS
# --------------------------------------------------

print("Loading MobileNetV2...")

mobilenet_model = tf.keras.models.load_model(
    MOBILENET_PATH,
    compile=False
)

print("MobileNetV2 loaded successfully.")

print("Loading EfficientNetB0...")

efficientnet_model = tf.keras.models.load_model(
    EFFICIENTNET_PATH,
    compile=False
)

print("EfficientNetB0 loaded successfully.")


# --------------------------------------------------
# IMAGE PREPROCESSING
# --------------------------------------------------

def prepare_image(image_path):

    with Image.open(image_path) as img:

        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")

        img = img.resize(
            IMAGE_SIZE,
            Image.Resampling.BILINEAR
        )

        image_array = np.asarray(
            img, dtype=np.float32
        )

    return image_array


# --------------------------------------------------
# MOBILENETV2 PREDICTION
# --------------------------------------------------

def predict_mobilenet(image_array):

    image = np.expand_dims(
        image_array.copy(), axis=0
    )

    image = tf.keras.applications.mobilenet_v2.preprocess_input(
        image
    )

    probabilities = mobilenet_model.predict(
        image, verbose=0
    )[0]

    index = int(np.argmax(probabilities))

    return {
        "model": "MobileNetV2",
        "predicted_class": CLASS_NAMES[index],
        "confidence": float(probabilities[index]),
        "probabilities": probabilities.tolist()
    }


# --------------------------------------------------
# EFFICIENTNETB0 PREDICTION
# --------------------------------------------------

def predict_efficientnet(image_array):

    image = np.expand_dims(
        image_array.copy(), axis=0
    )

    # EfficientNetB0 includes its own rescaling.
    # Keep input pixels in the 0-255 range.

    probabilities = efficientnet_model.predict(
        image, verbose=0
    )[0]

    index = int(np.argmax(probabilities))

    return {
        "model": "EfficientNetB0",
        "predicted_class": CLASS_NAMES[index],
        "confidence": float(probabilities[index]),
        "probabilities": probabilities.tolist()
    }


# --------------------------------------------------
# COMBINED PREDICTION
# --------------------------------------------------

def predict_both(image_path):

    if not os.path.isfile(image_path):
        raise FileNotFoundError("Image file not found.")

    image_array = prepare_image(image_path)

    mobile_result = predict_mobilenet(image_array)

    efficient_result = predict_efficientnet(image_array)

    agreement = (
        mobile_result["predicted_class"]
        == efficient_result["predicted_class"]
    )

    return {
        "mobilenet": mobile_result,
        "efficientnet": efficient_result,
        "models_agree": agreement
    }


print("FreshVision AI Engine initialized.")
print("Number of classes:", NUM_CLASSES)
