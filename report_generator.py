
from datetime import datetime, timezone
from pathlib import Path
import os

from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether
)

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

REPORT_DIR = Path("generated_reports")
REPORT_DIR.mkdir(exist_ok=True)

NAVY = colors.HexColor("#17263A")
GREEN = colors.HexColor("#10B981")
CYAN = colors.HexColor("#22D3EE")
LIGHT = colors.HexColor("#EAF2F8")
DARK = colors.HexColor("#263445")


# --------------------------------------------------
# STYLES
# --------------------------------------------------

def get_report_styles():

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=18,
        textColor=GREEN,
        spaceBefore=14,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        textColor=DARK
    ))

    return styles


# --------------------------------------------------
# TABLE GENERATOR
# --------------------------------------------------

def make_table(data, widths=None):

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    return table


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

def add_footer(canvas, doc):

    canvas.saveState()

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)

    canvas.drawString(
        18 * mm,
        12 * mm,
        "FreshVision AI | Research Analysis"
    )

    canvas.drawRightString(
        192 * mm,
        12 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# --------------------------------------------------
# CHART GENERATORS
# --------------------------------------------------

def create_bar_chart(labels, values, title, y_max=100):

    drawing = Drawing(450, 220)

    chart = VerticalBarChart()

    chart.x = 55
    chart.y = 45
    chart.height = 135
    chart.width = 350

    chart.data = [values]

    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 8

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = y_max
    chart.valueAxis.valueStep = max(1, y_max / 5)

    chart.bars[0].fillColor = GREEN
    chart.bars[0].strokeColor = NAVY

    chart.valueAxis.labels.fontSize = 8

    drawing.add(chart)

    return drawing


def create_grouped_chart(labels, datasets, y_max=100):

    drawing = Drawing(450, 230)

    chart = VerticalBarChart()

    chart.x = 55
    chart.y = 45
    chart.height = 140
    chart.width = 350

    chart.data = datasets

    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 8

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = y_max
    chart.valueAxis.valueStep = 20

    chart.groupSpacing = 12
    chart.barSpacing = 3

    chart.bars[0].fillColor = GREEN
    chart.bars[1].fillColor = CYAN
    chart.bars[2].fillColor = NAVY

    drawing.add(chart)

    return drawing


def create_dataset_chart():

    drawing = Drawing(400, 230)

    pie = Pie()

    pie.x = 100
    pie.y = 30
    pie.width = 180
    pie.height = 180

    pie.data = [12912, 2764, 2776]

    pie.labels = [
        "Training",
        "Validation",
        "Testing"
    ]

    pie.slices[0].fillColor = GREEN
    pie.slices[1].fillColor = CYAN
    pie.slices[2].fillColor = NAVY

    drawing.add(pie)

    return drawing


# --------------------------------------------------
# EXPLANATION IMAGE HANDLER
# --------------------------------------------------

def add_explanation_image(story, image_path, title, styles):

    if not image_path:
        story.append(Paragraph(
            f"{title}: Image unavailable.",
            styles["ReportBody"]
        ))
        return

    image_path = Path(image_path)

    if not image_path.is_file():
        story.append(Paragraph(
            f"{title}: Image unavailable.",
            styles["ReportBody"]
        ))
        return

    try:

        with PILImage.open(image_path) as img:
            img.verify()

        pdf_image = Image(
            str(image_path),
            width=75 * mm,
            height=65 * mm,
            kind="proportional"
        )

        story.append(KeepTogether([
            Paragraph(title, styles["SectionHeading"]),
            pdf_image,
            Spacer(1, 10)
        ]))

    except Exception:

        story.append(Paragraph(
            f"{title}: Unable to include image.",
            styles["ReportBody"]
        ))


# --------------------------------------------------
# INDIVIDUAL PREDICTION REPORT
# --------------------------------------------------

def generate_individual_report(report_data, output_path):

    styles = get_report_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm
    )

    story = []

    results = report_data.get("results", {})

    mobile = results.get("mobilenet", {})
    efficient = results.get("efficientnet", {})

    story.append(Paragraph(
        "FreshVision AI",
        styles["ReportTitle"]
    ))

    story.append(Paragraph(
        "Individual Fruit Quality Analysis Report",
        styles["Heading2"]
    ))

    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y, %H:%M UTC')}",
        styles["ReportBody"]
    ))

    story.append(Paragraph(
        "Prediction Results",
        styles["SectionHeading"]
    ))

    table_data = [
        ["Parameter", "MobileNetV2", "EfficientNetB0"],
        [
            "Predicted class",
            str(mobile.get("predicted_class", "N/A")),
            str(efficient.get("predicted_class", "N/A"))
        ],
        [
            "Confidence",
            f"{float(mobile.get('confidence', 0)):.2f}%",
            f"{float(efficient.get('confidence', 0)):.2f}%"
        ]
    ]

    story.append(make_table(
        table_data,
        [55 * mm, 55 * mm, 55 * mm]
    ))

    agreement = report_data.get("models_agree")

    agreement_text = (
        "Both models predicted the same class."
        if agreement is True
        else "The models predicted different classes."
        if agreement is False
        else "Agreement information unavailable."
    )

    story.append(Paragraph(
        "Model Agreement",
        styles["SectionHeading"]
    ))

    story.append(Paragraph(
        agreement_text,
        styles["ReportBody"]
    ))

    # XAI visualizations

    story.append(PageBreak())

    story.append(Paragraph(
        "Explainable AI Analysis",
        styles["ReportTitle"]
    ))

    explanations = report_data.get("explanations", {})

    image_mapping = [
        ("mobilenet_gradcam", "MobileNetV2 - Grad-CAM"),
        ("efficientnet_gradcam", "EfficientNetB0 - Grad-CAM"),
        ("mobilenet_lime", "MobileNetV2 - LIME"),
        ("efficientnet_lime", "EfficientNetB0 - LIME")
    ]

    for key, title in image_mapping:

        explanation = explanations.get(key, {})

        add_explanation_image(
            story,
            explanation.get("local_path"),
            title,
            styles
        )

    story.append(Paragraph(
        "Research Interpretation and Limitations",
        styles["SectionHeading"]
    ))

    story.append(Paragraph(
        "Grad-CAM provides a visual representation of image regions "
        "influencing the model prediction. LIME provides a local "
        "feature-based explanation of the individual prediction. "
        "These visualizations help interpret model behaviour but do "
        "not establish causal relationships.",
        styles["ReportBody"]
    ))

    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The reported confidence values represent model confidence, "
        "not a guarantee of actual fruit freshness or food safety. "
        "Predictions should be treated as research estimates and "
        "should not replace laboratory testing or expert assessment.",
        styles["ReportBody"]
    ))

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    return str(output_path)


# --------------------------------------------------
# MODEL EVALUATION REPORT
# --------------------------------------------------

def generate_evaluation_report(output_path):

    styles = get_report_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm
    )

    story = []

    story.append(Paragraph(
        "FreshVision AI",
        styles["ReportTitle"]
    ))

    story.append(Paragraph(
        "Comparative Model Evaluation Report",
        styles["Heading2"]
    ))

    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y, %H:%M UTC')}",
        styles["ReportBody"]
    ))

    # Dataset overview

    story.append(Paragraph(
        "Dataset Overview",
        styles["SectionHeading"]
    ))

    dataset_data = [
        ["Parameter", "Value"],
        ["Total images", "18,452"],
        ["Number of classes", "12"],
        ["Number of fruit types", "6"],
        ["Training images", "12,912"],
        ["Validation images", "2,764"],
        ["Testing images", "2,776"]
    ]

    story.append(make_table(
        dataset_data,
        [75 * mm, 75 * mm]
    ))

    # Dataset distribution chart

    story.append(Paragraph(
        "Dataset Split Distribution",
        styles["SectionHeading"]
    ))

    story.append(create_dataset_chart())

    # Model performance

    story.append(Paragraph(
        "Model Performance",
        styles["SectionHeading"]
    ))

    performance_data = [
        ["Metric", "MobileNetV2", "EfficientNetB0"],
        ["Accuracy", "98.13%", "98.63%"],
        ["Macro Precision", "97.53%", "98.13%"],
        ["Macro Recall", "97.84%", "98.20%"],
        ["Macro F1-score", "0.9768", "0.9816"],
        ["Weighted F1-score", "0.9813", "0.9863"]
    ]

    story.append(make_table(
        performance_data,
        [55 * mm, 55 * mm, 55 * mm]
    ))

    # Accuracy chart

    story.append(Paragraph(
        "Accuracy Comparison",
        styles["SectionHeading"]
    ))

    story.append(create_bar_chart(
        ["MobileNetV2", "EfficientNetB0"],
        [98.13, 98.63],
        "Accuracy"
    ))

    # Precision recall F1 chart

    story.append(PageBreak())

    story.append(Paragraph(
        "Precision, Recall and F1 Comparison",
        styles["SectionHeading"]
    ))

    story.append(create_grouped_chart(
        ["MobileNetV2", "EfficientNetB0"],
        [
            [97.53, 98.13],
            [97.84, 98.20],
            [97.68, 98.16]
        ]
    ))

    # Inference time

    story.append(Paragraph(
        "Inference Time Comparison",
        styles["SectionHeading"]
    ))

    inference_data = [
        ["Model", "Total time for 2,776 images"],
        ["MobileNetV2", "45.68 seconds"],
        ["EfficientNetB0", "58.77 seconds"]
    ]

    story.append(make_table(
        inference_data,
        [75 * mm, 75 * mm]
    ))

    story.append(create_bar_chart(
        ["MobileNetV2", "EfficientNetB0"],
        [45.68, 58.77],
        "Inference Time",
        y_max=70
    ))

    # Research observations

    story.append(Paragraph(
        "Research Observations",
        styles["SectionHeading"]
    ))

    story.append(Paragraph(
        "EfficientNetB0 achieved higher accuracy and recorded "
        "evaluation metrics in the experiment. MobileNetV2 "
        "completed the measured test-set inference faster. "
        "Model selection should consider both predictive "
        "performance and computational requirements.",
        styles["ReportBody"]
    ))

    story.append(Paragraph(
        "Limitations",
        styles["SectionHeading"]
    ))

    story.append(Paragraph(
        "These results describe the evaluated dataset and "
        "experimental setup. They do not establish equivalent "
        "performance in every real-world imaging environment. "
        "Dataset composition, image quality and external "
        "validation should be considered.",
        styles["ReportBody"]
    ))

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    return str(output_path)
