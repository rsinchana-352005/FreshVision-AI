
document.addEventListener("DOMContentLoaded", () => {

    if (typeof Chart === "undefined") {
        console.error("Chart.js could not be loaded.");
        return;
    }

    Chart.defaults.color = "#94A3B8";
    Chart.defaults.font.family = "Inter, sans-serif";

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    usePointStyle: true,
                    padding: 18
                }
            }
        }
    };

    // Dataset distribution
    new Chart(document.getElementById("datasetChart"), {
        type: "doughnut",
        data: {
            labels: ["Training", "Validation", "Testing"],
            datasets: [{
                data: [12912, 2764, 2776],
                backgroundColor: ["#10B981", "#22D3EE", "#A78BFA"],
                borderColor: "#17263A",
                borderWidth: 4,
                hoverOffset: 8
            }]
        },
        options: {
            ...commonOptions,
            cutout: "68%"
        }
    });

    // Classification metrics
    new Chart(document.getElementById("metricsChart"), {
        type: "bar",
        data: {
            labels: ["Precision", "Recall", "Macro F1"],
            datasets: [
                {
                    label: "MobileNetV2",
                    data: [97.53, 97.84, 97.68],
                    backgroundColor: "#22D3EE",
                    borderRadius: 6
                },
                {
                    label: "EfficientNetB0",
                    data: [98.13, 98.20, 98.16],
                    backgroundColor: "#10B981",
                    borderRadius: 6
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    min: 90,
                    max: 100,
                    title: {
                        display: true,
                        text: "Score (%)"
                    }
                }
            }
        }
    });

    // Total inference time
    new Chart(document.getElementById("inferenceChart"), {
        type: "bar",
        data: {
            labels: ["MobileNetV2", "EfficientNetB0"],
            datasets: [{
                label: "Total inference time (seconds)",
                data: [45.68, 58.77],
                backgroundColor: ["#22D3EE", "#10B981"],
                borderRadius: 7
            }]
        },
        options: {
            ...commonOptions,
            indexAxis: "y",
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Seconds"
                    }
                }
            }
        }
    });

    if (window.lucide) {
        lucide.createIcons();
    }

});
