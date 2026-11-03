# Heart Disease Prediction

A small REST API that predicts whether a patient has heart disease from 13 clinical measurements. The model is a scikit-learn logistic regression (with feature scaling) trained on the UCI heart disease data, and it is served with FastAPI and packaged with Docker so it can be deployed on Render.

Dataset: https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset (1025 rows, `target` = 1 means heart disease)

Live URL: <add Render URL here>

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app and endpoints
│   └── schemas.py         # request / response models
├── data/
│   └── heart.csv          # dataset
├── model/
│   └── heart_model.joblib # trained pipeline (committed)
├── train.py               # training script
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Features

| Feature | Description | Allowed values |
| --- | --- | --- |
| age | Age in years | 1 - 120 |
| sex | 1 = male, 0 = female | 0, 1 |
| cp | Chest pain type | 0 - 3 |
| trestbps | Resting blood pressure (mm Hg) | 50 - 250 |
| chol | Serum cholesterol (mg/dl) | 50 - 700 |
| fbs | Fasting blood sugar > 120 mg/dl | 0, 1 |
| restecg | Resting ECG result | 0 - 2 |
| thalach | Maximum heart rate achieved | 50 - 250 |
| exang | Exercise induced angina | 0, 1 |
| oldpeak | ST depression induced by exercise | 0 - 10 (decimal) |
| slope | Slope of the peak exercise ST segment | 0 - 2 |
| ca | Major vessels colored by fluoroscopy | 0 - 4 |
| thal | Thalassemia type | 0 - 3 |

Requests with a missing field or a value outside these ranges get a `422` response.

## Training

```
pip install -r requirements.txt
python train.py
```

The script splits the data 80/20 (`random_state=42`, stratified), fits a `StandardScaler` + `LogisticRegression` pipeline, prints the test metrics and saves the pipeline to `model/heart_model.joblib`.

On my run the test accuracy was 0.8098 (about 81%), with recall of 0.91 for the "disease" class and 0.70 for the "no disease" class.

The trained model file is committed, so you only need to run `train.py` again if you want to retrain.

## Running locally (without Docker)

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is then available at http://localhost:8000. By default the model is loaded from `model/heart_model.joblib`; set the `MODEL_PATH` environment variable to load a different file.

## Running with Docker

```
docker-compose build
docker-compose up
```

Swagger UI: http://localhost:8000/docs

The image only contains `app/` and `model/` (the dataset is not copied in). The container listens on `$PORT` if it is set, otherwise on 8000.

## Endpoints

### GET /health

```
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

### GET /info

```
curl http://localhost:8000/info
```

```json
{
  "model_type": "LogisticRegression",
  "features": ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"],
  "target": "heart disease (1 = disease, 0 = no disease)"
}
```

### POST /predict

```
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 52, "sex": 1, "cp": 0, "trestbps": 125, "chol": 212, "fbs": 0, "restecg": 1, "thalach": 168, "exang": 0, "oldpeak": 1.0, "slope": 2, "ca": 2, "thal": 3}'
```

```json
{"heart_disease": false, "probability": 0.2261}
```

`probability` is the model's probability of heart disease (rounded to 4 decimals) and `heart_disease` is the predicted class.

`GET /` redirects to the Swagger docs at `/docs`.

## Deploying on Render

1. Push the repo to GitHub (make sure `model/heart_model.joblib` is included).
2. On Render, click New > Web Service and connect the GitHub repo.
3. Choose Docker as the environment/language. Leave the root directory empty so the build context is the repo root, and the Dockerfile path as `./Dockerfile`.
4. Create the service. Render sets the `PORT` variable and the Dockerfile `CMD` uses it.
5. Once it is live, open `<your-url>/docs` to try the API and paste the URL in the "Live URL" line at the top of this file.
