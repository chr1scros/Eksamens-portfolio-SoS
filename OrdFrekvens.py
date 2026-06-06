import os
import csv
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab', quiet=True) 

def tæl_ord_med_nltk(mappe_sti, søgeord):
    resultater = []
    
    if not os.path.isdir(mappe_sti):
        print(f"Fejl: Mappen '{mappe_sti}' findes ikke.")
        return []
    stemmer = SnowballStemmer("danish")
    
    # Find roden (stammen) af de 5 søgeord på forhånd
    søgeord_stammer = {ordet: stemmer.stem(ordet.lower()) for ordet in søgeord}

    fil_liste = [f for f in os.listdir(mappe_sti) if f.endswith('.txt')]
    
    if not fil_liste:
        print(f"Fandt ingen .txt filer.")
        return []
        
    print(f"Fandt {len(fil_liste)} .txt filer. Analyserer med NLTK...")
    
    for filnavn in fil_liste:
        fuld_sti = os.path.join(mappe_sti, filnavn)
        tællinger = {ordet: 0 for ordet in søgeord}
        
        try:
            # Læs filen og håndter de danske tegn-fejl (utf-8 vs windows-1252)
            try:
                with open(fuld_sti, 'r', encoding='utf-8') as f:
                    indhold = f.read().lower()
            except UnicodeDecodeError:
                with open(fuld_sti, 'r', encoding='windows-1252') as f:
                    indhold = f.read().lower()
            
            # Del teksten op i rigtige ord (tokens)
            ord_i_tekst = word_tokenize(indhold, language='danish')
            
            # Find stammen for alle ord i teksten (vi ignorerer tegnsætning med .isalpha())
            stammer_i_tekst = [stemmer.stem(ordet) for ordet in ord_i_tekst if ordet.isalpha()]
            
            # Tæl hvor mange gange stammen af vores søgeord optræder i teksten
            for original_ord, søgeord_stamme in søgeord_stammer.items():
                tællinger[original_ord] = stammer_i_tekst.count(søgeord_stamme)
            
            resultater.append({
                'Dokument': filnavn,
                **tællinger
            })
            
        except Exception as e:
            print(f"Fejl ved læsning af {filnavn}: {e}")
            
    return resultater


min_mappe = r"tekster" 

# De 5 ord
termer = ['forsikring', 'køretøj', 'redningshjælp', 'tyveri', 'udland']

data = tæl_ord_med_nltk(min_mappe, termer)

if data:
    output_fil = os.path.join(min_mappe, 'ordfrekvens_nltk_resultat.csv')
    
    # Formatere kolonneoverskrifterne
    feltnavne = ['Dokument'] + [f"Term {i+1}: {term}" for i, term in enumerate(termer)]
    
    with open(output_fil, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        
        # Overskrifter
        writer.writerow(feltnavne)
        
        # Data
        for række in data:
            værdier = [række['Dokument']] + [række[term] for term in termer]
            writer.writerow(værdier)
            
    print(f"Færdig! Det meget mere præcise resultat er gemt i: {output_fil}")