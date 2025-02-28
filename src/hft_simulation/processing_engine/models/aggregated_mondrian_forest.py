from river.forest.aggregated_mondrian_forest import AMFClassifier

from src.hft_simulation.processing_engine.models.online_model import OnlineModel

class AggregatedMondrianForest(OnlineModel):
    """
    https://riverml.xyz/latest/api/forest/AMFClassifier/
    """

    def __init__(self):
        super().__init__()
        
        self.model = AMFClassifier(
            n_estimators=10,
            use_aggregation=True,
            dirichlet=0.5, # 1 / n_classes
            seed=42
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'n_estimators={self.model.n_estimators}, ' \
               f'use_aggregation={self.model.use_aggregation}, ' \
               f'dirichlet={self.model.dirichlet}, ' \
               f'seed={self.model.seed})'
    
    def fit(self, X: dict[str, float], y: int) -> None:
        self.model.learn_one(X, y)

    def predict(self, X: dict[str, float]) -> int | None:
        return self.model.predict_one(X)
