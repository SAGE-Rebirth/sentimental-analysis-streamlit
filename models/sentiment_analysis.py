from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

def analyze_sentiment_with_stars(text):
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        scores = outputs[0][0].detach().numpy()
        probabilities = torch.nn.functional.softmax(torch.tensor(scores), dim=0).tolist()
        star_rating = int(np.argmax(probabilities) + 1)
        if star_rating in [1, 2]:
            sentiment_label = "Negative"
        elif star_rating == 3:
            sentiment_label = "Neutral"
        else:
            sentiment_label = "Positive"
        return star_rating, sentiment_label, probabilities
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return None, None, []