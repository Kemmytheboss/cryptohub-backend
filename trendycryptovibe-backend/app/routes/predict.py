from app.ai.predictor import prediction
from fastapi import APIRouter
from typing import List

router = APIRouter(prefix='/predict', tags=["AI"])

@router.post("/")
def predict_price(prices: List[float]):
    """
    Send a list of last market prices:
    example:
    {
        "prices: [100, 103, 104, 102, 105]
    }
    """
    result = siple_prediction(prices)
    return{"signal": result}
