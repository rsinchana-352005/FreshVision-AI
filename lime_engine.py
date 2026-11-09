
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import tensorflow as tf

from lime.lime_image import LimeImageExplainer
from skimage.segmentation import mark_boundaries

from ai_engine import (
    mobilenet_model,
    efficientnet_model,
    CLASS_NAMES
)


# =====================================================
# CONFIGURATION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LIME_OUTPUT_DIR = os.path.join(
    BASE_DIR, "uploads", "xai"
)

os.makedirs(LIME_OUTPUT_DIR, exist_ok=True)

IMAGE_SIZE = (224, 224)
NUM_SAMPLES = 500
BATCH_SIZE = 16


# =====================================================
# LIME EXPLAINER
# =====================================================

explainer = LimeImageExplainer(random_state=42)


# =====================================================
# MOBILENETV2 PREDICTION FUNCTION
# =====================================================

def predict_mobilenet_images(images):

    images = np.asarray(images, dtype=np.float32)

    processed = (
        tf.keras.applications.mobilenet_v2
        .preprocess_input(images.copy())
    )

    return mobilenet_model.predict(
        processed,
        batch_size=BATCH_SIZE,
        verbose=0
    )


# =====================================================
# EFFICIENTNETB0 PREDICTION FUNCTION
# =====================================================

def predict_efficientnet_images(images):

    images = np.asarray(images, dtype=np.float32)

    # Preserve raw RGB values from 0 to 255.
    # EfficientNetB0 includes built-in rescaling.

    return efficientnet_model.predict(
        images,
        batch_size=BATCH_SIZE,
        verbose=0
    )


# =====================================================
# GENERIC LIME EXPLANATION
# =====================================================

def generate_lime_explanation(
    image_array,
    prediction_function,
    model_name,
    output_path
):

    image_array = np.clip(
        image_array, 0, 255
    ).astype(np.uint8)

    print(f"Generating LIME for {model_name}...")

    # Original prediction
    predictions = prediction_function(
        image_array[np.newaxis, ...]
    )[0]

    predicted_index = int(np.argmax(predictions))

    predicted_class = CLASS_NAMES[predicted_index]

    confidence = float(
        predictions[predicted_index]
    ) * 100

    # Generate explanation
    explanation = explainer.explain_instance(
        image=image_array,
        classifier_fn=prediction_function,
        top_labels=1,
        hide_color=0,
        num_samples=NUM_SAMPLES
    )

    label = explanation.top_labels[0]

    explained_image, mask = (
        explanation.get_image_and_mask(
            label=label,
            positive_only=False,
            num_features=10,
            hide_rest=False
        )
    )

    # Visualization
    fig, axes = plt.subplots(
        1, 3, figsize=(15, 5)
    )

    axes[0].imshow(image_array)
    axes[0].set_title("Original Image")

    axes[1].imshow(mask, cmap="bwr")
    axes[1].set_title("LIME Feature Mask")

    axes[2].imshow(
        mark_boundaries(
            explained_image,
            mask
        )
    )
    axes[2].set_title("LIME Explanation")

    for ax in axes:
        ax.axis("off")

    fig.suptitle(
        f"{model_name}: {predicted_class} "
        f"({confidence:.2f}%)"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"{model_name} LIME saved: {output_path}")

    return {
        "model": model_name,
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "image_path": output_path
    }


# =====================================================
# MOBILENETV2 LIME
# =====================================================

def generate_mobilenet_lime(image_array, unique_id):

    output_path = os.path.join(
        LIME_OUTPUT_DIR,
        f"{unique_id}_mobilenet_lime.png"
    )

    return generate_lime_explanation(
        image_array,
        predict_mobilenet_images,
        "MobileNetV2",
        output_path
    )


# =====================================================
# EFFICIENTNETB0 LIME
# =====================================================

def generate_efficientnet_lime(image_array, unique_id):

    output_path = os.path.join(
        LIME_OUTPUT_DIR,
        f"{unique_id}_efficientnet_lime.png"
    )

    return generate_lime_explanation(
        image_array,
        predict_efficientnet_images,
        "EfficientNetB0",
        output_path
    )


# =====================================================
# COMBINED LIME
# =====================================================

def generate_both_lime(image_array, unique_id):

    mobile_result = generate_mobilenet_lime(
        image_array,
        unique_id
    )

    efficient_result = generate_efficientnet_lime(
        image_array,
        unique_id
    )

    return {
        "mobilenet_lime": mobile_result,
        "efficientnet_lime": efficient_result
    }


print("FreshVision AI LIME engine initialized.")
