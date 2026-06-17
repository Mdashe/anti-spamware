from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.predict import SpamClassifier
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title='SA Spam Classifier')


Instrumentator().instrument(app).expose(app)
g


classifier = SpamClassifier(stage='Production')

class EmailRequest(BaseModel):
    subject: str = ''
    body:    str = ''
    model:   str = 'ensemble'


@app.post('/predict')
def predict(email: EmailRequest):
    try:
        r = classifier.predict(
            subject=email.subject,
            body=email.body,
            model=email.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return r.__dict__

@app.get('/health')
def health():
    return {'status': 'ok'}
