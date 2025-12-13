def format_prediction(label):
    emotions = {
        "anxiety": "Ansiedad",
        "stress": "Estrés",
        "positive": "Estado Positivo",
        "neutral": "Neutro"
    }
    return emotions.get(label, label)
