from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

# Load the pre-trained model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def analyze_sentiment_with_stars(text):
    try:
        # Tokenize input text and move to GPU
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)

        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)
            scores = outputs.logits[0].detach().cpu().numpy()  # Move scores back to CPU for processing

        # Calculate probabilities and star rating
        probabilities = torch.nn.functional.softmax(torch.tensor(scores), dim=0).tolist()
        star_rating = int(np.argmax(probabilities) + 1)

        # Map star rating to sentiment label
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

# # Example usage
# text = "यह बहुत अच्छा ब्लॉग पोस्ट है! मैंने इसे पढ़कर बहुत आनंद लिया।"
# star_rating, sentiment_label, probabilities = analyze_sentiment_with_stars(text)
# print(f"Star Rating: {star_rating}, Sentiment: {sentiment_label}, Probabilities: {probabilities}")