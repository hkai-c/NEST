from typing import List, Dict, Any
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import emoji
from transformers import AutoTokenizer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

logger = logging.getLogger(__name__)

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.is_fitted = False

    def preprocess_text(self, text: str) -> str:
        """Apply basic text preprocessing."""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove special characters and numbers
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\d+', '', text)
            
            # Convert emojis to text
            text = emoji.demojize(text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            return text
        except Exception as e:
            logger.error(f"Error in basic preprocessing: {str(e)}")
            return text

    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """Tokenize and lemmatize text."""
        try:
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and lemmatize
            tokens = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words and len(token) > 2
            ]
            
            return tokens
        except Exception as e:
            logger.error(f"Error in tokenization and lemmatization: {str(e)}")
            return []

    def get_bert_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get BERT embeddings for texts."""
        try:
            # Tokenize and prepare for BERT
            encoded = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors='pt'
            )
            
            # Convert to numpy array (placeholder for actual BERT model)
            # In practice, you would use a BERT model to get embeddings
            return np.random.rand(len(texts), 768)  # 768 is BERT's embedding size
        except Exception as e:
            logger.error(f"Error getting BERT embeddings: {str(e)}")
            return np.array([])

    def get_tfidf_features(self, texts: List[str]) -> np.ndarray:
        """Get TF-IDF features for texts."""
        try:
            # Preprocess texts
            processed_texts = [self.preprocess_text(text) for text in texts]
            
            # Fit and transform if not already fitted
            if not self.is_fitted:
                features = self.tfidf_vectorizer.fit_transform(processed_texts)
                self.is_fitted = True
            else:
                features = self.tfidf_vectorizer.transform(processed_texts)
            
            return features.toarray()
        except Exception as e:
            logger.error(f"Error getting TF-IDF features: {str(e)}")
            return np.array([])

    def get_combined_features(
        self,
        texts: List[str],
        use_bert: bool = True,
        use_tfidf: bool = True
    ) -> np.ndarray:
        """Get combined features from multiple methods."""
        try:
            features = []
            
            if use_bert:
                bert_features = self.get_bert_embeddings(texts)
                features.append(bert_features)
            
            if use_tfidf:
                tfidf_features = self.get_tfidf_features(texts)
                features.append(tfidf_features)
            
            if not features:
                raise ValueError("At least one feature extraction method must be enabled")
            
            # Combine features
            return np.hstack(features)
        except Exception as e:
            logger.error(f"Error getting combined features: {str(e)}")
            return np.array([])

    def get_vocabulary(self) -> Dict[str, int]:
        """Get the vocabulary from the TF-IDF vectorizer."""
        try:
            if not self.is_fitted:
                return {}
            return self.tfidf_vectorizer.vocabulary_
        except Exception as e:
            logger.error(f"Error getting vocabulary: {str(e)}")
            return {}

    def save_preprocessor(self, path: str):
        """Save the preprocessor state."""
        try:
            import pickle
            with open(path, 'wb') as f:
                pickle.dump({
                    'tfidf_vectorizer': self.tfidf_vectorizer,
                    'is_fitted': self.is_fitted
                }, f)
        except Exception as e:
            logger.error(f"Error saving preprocessor: {str(e)}")
            raise

    def load_preprocessor(self, path: str):
        """Load the preprocessor state."""
        try:
            import pickle
            with open(path, 'rb') as f:
                state = pickle.load(f)
                self.tfidf_vectorizer = state['tfidf_vectorizer']
                self.is_fitted = state['is_fitted']
        except Exception as e:
            logger.error(f"Error loading preprocessor: {str(e)}")
            raise 