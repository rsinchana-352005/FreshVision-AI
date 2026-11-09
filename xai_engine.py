
import os
import numpy as np
import tensorflow as tf
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from ai_engine import (
    mobilenet_model,
    efficientnet_model,
    CLASS_NAMES
)

from PIL import Image


# =====================================================
# CONFIGURATION
# =====================================================

IMAGE_SIZE = (224, 224)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

XAI_OUTPUT_DIR = os.path.join(
    BASE_DIR, "uploads", "xai"
)

os.makedirs(XAI_OUTPUT_DIR, exist_ok=True)


# =====================================================
# MOBILENETV2 GRAD-CAM CONNECTION
# =====================================================

mobile_backbone = mobilenet_model.get_layer(
    "mobilenetv2_1.00_224"
)

mobile_last_conv = mobile_backbone.get_layer(
    "out_relu"
)

mobile_conv_model = tf.keras.Model(
    inputs=mobile_backbone.input,
    outputs=mobile_last_conv.output
)

mobile_input = mobilenet_model.input

mobile_conv_outputs = mobile_conv_model(
    mobile_input, training=False
)

x = mobile_conv_outputs

for layer in mobilenet_model.layers[2:]:
    x = layer(x)

mobile_grad_model = tf.keras.Model(
    inputs=mobile_input,
    outputs=[mobile_conv_outputs, x]
)


# =====================================================
# EFFICIENTNETB0 GRAD-CAM CONNECTION
# =====================================================

efficient_backbone = next(
    layer for layer in efficientnet_model.layers
    if isinstance(layer, tf.keras.Model)
)

efficient_last_conv = efficient_backbone.get_layer(
    "top_conv"
)

efficient_grad_model = tf.keras.Model(
    inputs=efficient_backbone.input,
    outputs=[
        efficient_last_conv.output,
        efficient_backbone.output
    ]
)

efficient_classifier_layers = [
    layer for layer in efficientnet_model.layers
    if layer is not efficient_backbone
    and not isinstance(layer, tf.keras.layers.InputLayer)
]


# =====================================================
# VISUALIZATION FUNCTION
# =====================================================

def save_gradcam_visualization(
    original_image,
    heatmap,
    model_name,
    predicted_class,
    confidence,
    output_path
):

    fig, axes = plt.subplots(
        1, 3, figsize=(15, 5)
    )

    axes[0].imshow(original_image)
    axes[0].set_title("Original Image")

    axes[1].imshow(heatmap, cmap="jet")
    axes[1].set_title("Grad-CAM Heatmap")

    axes[2].imshow(original_image)
    axes[2].imshow(
        heatmap,
        cmap="jet",
        alpha=0.4
    )
    axes[2].set_title("Grad-CAM Overlay")

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

    return output_path


# =====================================================
# GENERIC GRAD-CAM CALCULATION
# =====================================================

def calculate_heatmap(
    grad_model,
    input_tensor,
    classifier_layers=None
):

    with tf.GradientTape() as tape:

        if classifier_layers is None:

            conv_outputs, predictions = grad_model(
                input_tensor,
                training=False
            )

        else:

            features, x = grad_model(
                input_tensor,
                training=False
            )

            for layer in classifier_layers:
                x = layer(x, training=False)

            predictions = x
            conv_outputs = features

        predicted_index = tf.argmax(
            predictions[0]
        )

        class_score = predictions[:, predicted_index]

    gradients = tape.gradient(
        class_score,
        conv_outputs
    )

    if gradients is None:
        raise ValueError(
            "Grad-CAM gradients could not be calculated."
        )

    weights = tf.reduce_mean(
        gradients,
        axis=(1, 2)
    )

    heatmap = tf.reduce_sum(
        conv_outputs[0] *
        weights[0][tf.newaxis, tf.newaxis, :],
        axis=-1
    )

    heatmap = tf.nn.relu(heatmap)

    heatmap = heatmap / (
        tf.reduce_max(heatmap) + 1e-8
    )

    heatmap = tf.image.resize(
        heatmap[..., tf.newaxis],
        IMAGE_SIZE
    ).numpy().squeeze()

    predicted_index = int(
        predicted_index.numpy()
    )

    confidence = float(
        predictions[0][predicted_index].numpy()
    ) * 100

    return (
        heatmap,
        predicted_index,
        confidence
    )


# =====================================================
# MOBILENETV2 GRAD-CAM
# =====================================================

def generate_mobilenet_gradcam(image_array, output_path):

    original_image = np.clip(
        image_array, 0, 255
    ).astype(np.uint8)

    processed = tf.keras.applications.mobilenet_v2.preprocess_input(
        image_array.copy()
    )

    input_tensor = np.expand_dims(
        processed, axis=0
    )

    heatmap, index, confidence = calculate_heatmap(
        mobile_grad_model,
        input_tensor
    )

    predicted_class = CLASS_NAMES[index]

    save_gradcam_visualization(
        original_image,
        heatmap,
        "MobileNetV2",
        predicted_class,
        confidence,
        output_path
    )

    return {
        "model": "MobileNetV2",
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "image_path": output_path
    }


# =====================================================
# EFFICIENTNETB0 GRAD-CAM
# =====================================================

def generate_efficientnet_gradcam(image_array, output_path):

    original_image = np.clip(
        image_array, 0, 255
    ).astype(np.uint8)

    input_tensor = np.expand_dims(
        image_array.copy().astype(np.float32),
        axis=0
    )

    heatmap, index, confidence = calculate_heatmap(
        efficient_grad_model,
        input_tensor,
        efficient_classifier_layers
    )

    predicted_class = CLASS_NAMES[index]

    save_gradcam_visualization(
        original_image,
        heatmap,
        "EfficientNetB0",
        predicted_class,
        confidence,
        output_path
    )

    return {
        "model": "EfficientNetB0",
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "image_path": output_path
    }


# =====================================================
# COMBINED GRAD-CAM
# =====================================================

def generate_both_gradcams(image_array, unique_id):

    mobile_path = os.path.join(
        XAI_OUTPUT_DIR,
        f"{unique_id}_mobilenet_gradcam.png"
    )

    efficient_path = os.path.join(
        XAI_OUTPUT_DIR,
        f"{unique_id}_efficientnet_gradcam.png"
    )

    mobile_result = generate_mobilenet_gradcam(
        image_array,
        mobile_path
    )

    efficient_result = generate_efficientnet_gradcam(
        image_array,
        efficient_path
    )

    return {
        "mobilenet_gradcam": mobile_result,
        "efficientnet_gradcam": efficient_result
    }


print("FreshVision AI Grad-CAM engine initialized.")
