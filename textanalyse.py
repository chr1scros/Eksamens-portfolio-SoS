import pandas as pd
import re

def load_sentiment_dict(file_path):
    """Indlæser sentimentleksikon fra CSV"""
    df = pd.read_csv(file_path, header=None)
    sentiment_map = {}
    for _, row in df.iterrows():
        score = row[4]
        forms = str(row[5]).split(';')
        for form in forms:
            if form.strip():
                sentiment_map[form.lower().strip()] = score
    return sentiment_map

emoji_sentiment = {
    "😊": 4, "😉": 2, "😁": 3, "🤩": 5, "😎": 2,
    "😢": -4, "😠": -5, "💀": -2, "🙄": -2, "😕": -2
}

def advanced_analyse(sentence, sentiment_dict):
    """Analyserer stemning med fokus på kontekst (negering) og emojis."""
    if pd.isna(sentence):
        return 0
    
    # Find alle ord og emojis (bruger regex til at fange unicode emojis)
    tokens = re.findall(r'\b\w+\b|[\U00010000-\U0010ffff]', sentence.lower())
    
    total_score = 0
        # bi-grams
    negation_words = {"ikke", "aldrig", "ingen", "ej", "hverken"}
    negate_next = False
    
    for token in tokens:
        score = 0
        
        # Emoji lookup
        if token in emoji_sentiment:
            score = emoji_sentiment[token]
        # Ordbogs lookup
        elif token in sentiment_dict:
            score = sentiment_dict[token]
            
        # Kontekst
        if negate_next:
            score = -score # Vend fortegnet (f.eks. "ikke god" bliver negativ)
            negate_next = False
            
        if token in negation_words:
            negate_next = True
            continue # Spring over selve negeringsordet
            
        total_score += score
            
    return total_score

def get_label(score):
    """Oversætter tal-score til en tekst-vurdering."""
    if score >= 1:
        return "Positiv"
    elif score <= -1:
        return "Negativ"
    else:
        return "Neutral"

# Indlæs ordbogen
dict_file = '2_headword_headword_polarity.csv'
sentiment_dict = load_sentiment_dict(dict_file)

# Indlæs filen med tekster (tweets)
input_file = 'Testing.csv'
tweets_df = pd.read_csv(input_file)

print(f"{'ID':<8} | {'Vurdering':<10} | {'Tekst snippet'}")
print("-" * 60)

# Loop gennem hver række i tweet-filen
for index, row in tweets_df.iterrows():
    tweet_id = row['original_tweet_index'] # Første kolonne
    text = row['text']                     # Anden kolonne
    
    # Beregn score
    score = advanced_analyse(text, sentiment_dict)
    vurdering = get_label(score)
    
    # Printer resultat (kun de første 50 tegn af teksten for overblik)
    print(f"{tweet_id:<8} | {vurdering:<10} | {str(text)[:50].replace(chr(10), ' ')}...")