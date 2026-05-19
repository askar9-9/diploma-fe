# Spec: Training, Model Store, And API

## Назначение

Подсистема обучения и хранения модели отвечает за автозагрузку последней версии классификатора при старте сервиса, автоматическое обучение на синтетических данных при отсутствии модели, ручное обучение через REST API и выдачу метаданных текущей модели.

## Контракт

```python
MODEL_PATH = os.getenv("MODEL_PATH", "data/models/")


def save_model(classifier) -> str:
    # Сохраняет модель в data/models/classifier_{timestamp}.joblib
    # Возвращает путь к файлу


def load_latest_model(classifier) -> bool:
    # Загружает последнюю модель из MODEL_PATH
    # Возвращает False, если файлов нет


GET  /health
    -> {"status": "ok", "model_loaded": bool}

POST /classify
    body: FeatureVector
    -> ClassificationResult

POST /cluster
    body: {"vectors": [...], "n_clusters": 4}
    -> ClusterResult

POST /suggest
    body: {"vectors": [...], "labels": [...], "known_scenarios": [...]}
    -> list[PatternSuggestion]

POST /train
    body: {"vectors": [...], "labels": [...]}
    -> {"accuracy": float, "version": str}

GET  /model/info
    -> {"version": str, "trained_at": str, "n_classes": int, "accuracy": float}
```

## Acceptance Tests

### Given / When / Then
- Given: сервис стартует и в `MODEL_PATH` нет моделей
- When: инициализируется приложение
- Then: выполняется автоматическое обучение на synthetic data и сервис возвращает `model_loaded=true`

- Given: обученный классификатор
- When: вызывается `save_model`, затем `load_latest_model`
- Then: загружается последняя версия `.joblib`

- Given: список feature vectors и labels
- When: вызывается `POST /train`
- Then: возвращаются `accuracy` и `version`, а модель сохраняется на диск

- Given: загруженная или обученная модель
- When: вызывается `GET /model/info`
- Then: ответ содержит `version`, `trained_at`, `n_classes`, `accuracy`
