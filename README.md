\# FreshVision AI 🍎



\### AI-Powered Fruit Quality Classification with Explainable Artificial Intelligence



FreshVision AI is a research-oriented web application that uses deep learning and Explainable AI (XAI) to classify fruit quality from images.



The system integrates two convolutional neural network architectures, MobileNetV2 and EfficientNetB0, with Grad-CAM and LIME to provide visual explanations for model predictions.



\## 🚀 Key Features



\- \*\*Dual-model prediction:\*\* Uses MobileNetV2 and EfficientNetB0 for fruit quality classification.

\- \*\*12-class classification:\*\* Identifies six fruit types across Good and Bad quality categories.

\- \*\*Explainable AI:\*\* Generates Grad-CAM heatmaps and LIME visual explanations.

\- \*\*Model comparison:\*\* Displays and compares predictions from both models.

\- \*\*Interactive dashboard:\*\* Provides prediction analytics and visualizations.

\- \*\*PDF reports:\*\* Generates downloadable prediction and evaluation reports.

\- \*\*User authentication:\*\* Registration, login and profile management.

\- \*\*Feedback system:\*\* Allows users to submit feedback.

\- \*\*Database integration:\*\* MongoDB Atlas for user and feedback data.



\## 🍊 Dataset



FreshVision AI uses a processed subset of the \*\*FruitNet: Indian Fruits Dataset with quality (Good, Bad \& Mixed quality)\*\*.



The original FruitNet dataset contains images of six Indian fruits:



\- Apple

\- Banana

\- Guava

\- Lime

\- Orange

\- Pomegranate



For this project, the Good and Bad quality categories are used, resulting in 12 classification classes. The Mixed quality category is excluded.



\### Dataset preparation



| Category | Details |

|---|---:|

| Total images | 18,452 |

| Classification classes | 12 |

| Training images | 12,912 |

| Validation images | 2,764 |

| Testing images | 2,776 |



The dataset was organized into training, validation and testing manifests for model development and evaluation.



\*\*Dataset attribution\*\*



Meshram, V., \& Patil, K. (2022). FruitNet: Indian fruits image dataset with quality for machine learning applications. \*Data in Brief, 40\*, 107686.



https://doi.org/10.1016/j.dib.2021.107686



\*\*Original dataset repository\*\*



Meshram, V., \& Patil, K. (2021). FruitNet: Indian Fruits Dataset with quality (Good, Bad \& Mixed quality). Mendeley Data, Version 1.



https://doi.org/10.17632/b6fftwbr2v.1



\*\*Dataset licence:\*\* Creative Commons Attribution 4.0 International (CC BY 4.0).



The original dataset creators retain attribution for the source images. The 12-class subset, preprocessing, manifests and model training are part of this project.



\## 🧠 Deep Learning Models



FreshVision AI uses two trained models:



| Model | Test Accuracy | Macro F1-score |

|---|---:|---:|

| MobileNetV2 | 98.13% | 0.9768 |

| EfficientNetB0 | 98.63% | 0.9816 |



These are the project's reported results on its internal test split. They should not be interpreted as guaranteed performance on all real-world fruit images.



\## 🔍 Explainable AI



The application integrates two explanation techniques:



\*\*Grad-CAM\*\*

\- Generates visual heatmaps.

\- Highlights image regions that contribute to model predictions.



\*\*LIME\*\*

\- Produces local, image-based explanations.

\- Highlights image regions that influence individual predictions.



Both techniques are integrated with the two trained classification models.



\## 🛠️ Technology Stack



| Component | Technology |

|---|---|

| Programming language | Python 3.11 |

| Backend | Flask |

| Frontend | HTML, CSS, JavaScript |

| Deep learning | TensorFlow / Keras |

| Models | MobileNetV2, EfficientNetB0 |

| Explainable AI | Grad-CAM, LIME |

| Image processing | Pillow, scikit-image |

| Data processing | NumPy, Pandas |

| Visualization | Matplotlib, Chart.js |

| PDF generation | ReportLab |

| Database | MongoDB Atlas |

| Deployment server | Gunicorn |



\## 📁 Project Structure



```text

FreshVision-AI/

│

├── app.py

├── database.py

├── ai\_engine.py

├── xai\_engine.py

├── lime\_engine.py

├── report\_generator.py

├── requirements.txt

├── .gitignore

│

├── models/

│   ├── mobilenetv2\_best.keras

│   └── efficientnetb0\_best.keras

│

├── manifests/

│   ├── fruitnet\_train\_windows.csv

│   ├── fruitnet\_validation\_windows.csv

│   └── fruitnet\_test\_windows.csv

│

├── templates/

│

└── static/

&#x20;   ├── css/

&#x20;   ├── js/

&#x20;   └── images/

```



\## ⚙️ Installation and Setup



\### 1. Clone the repository



```bash

git clone https://github.com/rsinchana-352005/FreshVision-AI.git

cd FreshVision-AI

```



\### 2. Create a virtual environment



```bash

python -m venv freshvision\_env

```



Activate it on Windows:



```cmd

freshvision\_env\\Scripts\\activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file in the project root:



```env

FLASK\_SECRET\_KEY=your-secret-key

MONGO\_URI=your-mongodb-connection-string

MONGO\_DATABASE=your-database-name

```



Use your own credentials. Never commit `.env` to GitHub.



\### 5. Run the application



```bash

python app.py

```



Open:



http://127.0.0.1:5000



\## 🔐 Security



\- Environment variables are used for application secrets and database credentials.

\- User authentication and CSRF protection are implemented.

\- Uploaded images are subject to file-size restrictions.

\- Sensitive configuration files are excluded from version control.



\## 📊 Research Scope



FreshVision AI explores the application of deep learning and explainability techniques to visual fruit quality classification.



The project focuses on:

\- Comparative evaluation of MobileNetV2 and EfficientNetB0.

\- Visual interpretation of model predictions.

\- Integration of AI models into a web-based research application.

\- Generation of prediction and evaluation reports.



\## 📚 References



1\. Meshram, V., \& Patil, K. (2022). FruitNet: Indian fruits image dataset with quality for machine learning applications. \*Data in Brief, 40\*, 107686. https://doi.org/10.1016/j.dib.2021.107686



2\. Meshram, V., \& Patil, K. (2021). FruitNet: Indian Fruits Dataset with quality (Good, Bad \& Mixed quality). Mendeley Data. https://doi.org/10.17632/b6fftwbr2v.1



\## 👩‍💻 Project



\*\*FreshVision AI\*\*  

An AI-powered fruit quality classification and explainability research project.



GitHub Repository: https://github.com/rsinchana-352005/FreshVision-AI

