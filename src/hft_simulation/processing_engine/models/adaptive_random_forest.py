from river.forest.adaptive_random_forest import ARFClassifier

from src.hft_simulation.processing_engine.models.online_model import OnlineModel

class AdaptiveRandomForest(OnlineModel):
    """
    https://riverml.xyz/latest/api/forest/ARFClassifier/
    """

    def __init__(self):
        super().__init__()
        
        self.model = ARFClassifier(
            models=10,
            leaf_prediction="mc",
            seed=42
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'models={self.model.models}, ' \
               f'leaf_prediction={self.model.leaf_prediction}, ' \
               f'seed={self.model.seed})'
    
    def fit(self, X: dict[str, float], y: int) -> None:
        self.model.learn_one(X, y)

    def predict(self, X: dict[str, float]) -> int | None:
        return self.model.predict_one(X)
