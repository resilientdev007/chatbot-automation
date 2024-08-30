from sentence_transformers import SentenceTransformer, util
import spacy
import pandas as pd
from fuzzywuzzy import fuzz
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import Levenshtein
import logging

# Set up logging
logging.basicConfig(filename='model_output.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SpaCy and SentenceTransformer
nlp = spacy.load('en_core_web_sm')
model = SentenceTransformer('all-MiniLM-L6-v2')

def _calculate_similarity(text1, text2):
    """
    Calculate the cosine similarity between two texts using SentenceTransformer.

    Args:
        text1 (str): The first text.
        text2 (str): The second text.

    Returns:
        float: The cosine similarity score.
    """
    try:
        embeddings1 = model.encode(text1, convert_to_tensor=True)
        embeddings2 = model.encode(text2, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
        return similarity.item()  # Return a single scalar value (float)
    except Exception as e:
        logging.error(f"Error calculating similarity: {e}")
        raise

def _calculate_levenshtein_similarity(text1, text2):
    """
    Calculate the Levenshtein similarity between two texts.

    Args:
        text1 (str): The first text.
        text2 (str): The second text.

    Returns:
        float: The Levenshtein similarity score.
    """
    try:
        distance = Levenshtein.distance(text1, text2)
        similarity = 1 - (distance / max(len(text1), len(text2)))
        return similarity
    except Exception as e:
        logging.error(f"Error calculating Levenshtein similarity: {e}")
        raise

def _extract_keywords(text):
    """
    Extract keywords from a given text using SpaCy.

    Args:
        text (str): The text from which to extract keywords.

    Returns:
        set: A set of keywords.
    """
    try:
        doc = nlp(text)
        keywords = set([
            token.lemma_.lower() for token in doc
            if not token.is_stop and not token.is_punct and len(token) > 1
        ])
        return keywords
    except Exception as e:
        logging.error(f"Error extracting keywords: {e}")
        raise

def validate_response(expected_answer, actual_response, config):
    """
    Validate the response by calculating various similarity metrics.

    Args:
        expected_answer (str): The expected answer.
        actual_response (str): The actual response.
        config (dict): Configuration dictionary containing thresholds and weights.

    Returns:
        tuple: A tuple containing similarity scores and match indicators.
    """
    try:
        # Extract keywords for single text pairs
        actual_keywords = _extract_keywords(actual_response)
        expected_keywords = _extract_keywords(expected_answer)

        # Calculate similarity score for the pair using BERT-based similarity
        similarity_score = _calculate_similarity(expected_answer, actual_response)

        # Compute keyword match
        keyword_match = len(expected_keywords.intersection(actual_keywords)) / len(expected_keywords) >= config['keyword_match_threshold']

        # Fuzzy match
        fuzzy_score = fuzz.ratio(expected_answer.lower(), actual_response.lower())
        fuzzy_match = fuzzy_score >= config['fuzzy_match_threshold']

        # Levenshtein similarity
        levenshtein_similarity = _calculate_levenshtein_similarity(expected_answer, actual_response)

        # Combined score using weighted average
        combined_score = (
            (similarity_score * config['weights']['similarity']) +
            (keyword_match * config['weights']['keyword_match']) +
            (fuzzy_match * config['weights']['fuzzy_match']) +
            (levenshtein_similarity * config['weights']['levenshtein_similarity'])
        ) / sum(config['weights'].values())

        return similarity_score, keyword_match, fuzzy_score, fuzzy_match, levenshtein_similarity, combined_score
    except Exception as e:
        logging.error(f"Error validating response: {e}")
        raise

def validate_expected_data(expected_data, actual_response):
    """
    Validate if the expected data is present in the actual response.

    Args:
        expected_data (str): The expected data.
        actual_response (str): The actual response.

    Returns:
        bool: True if expected data is in the actual response, False otherwise.
    """
    try:
        # Ensure both expected_data and actual_response are strings
        expected_data = str(expected_data).lower()
        actual_response = str(actual_response).lower()

        # Check if expected data is in the actual response
        return expected_data in actual_response
    except Exception as e:
        logging.error(f"Error validating expected data: {e}")
        raise

def generate_report(results_df, output_path, sheet_name):
    """
    Generate a report with accuracy, precision, recall, and F1-score.

    Args:
        results_df (pd.DataFrame): A DataFrame containing validation results.
        output_path (str): The path to the output Excel file.
        sheet_name (str): The name of the sheet in the Excel file.
    """
    try:
        # Convert match criteria to binary labels
        actual_labels = [1 if row['Keyword Match'] and row['Fuzzy Match'] and row['Expected Data Match'] else 0 for row in results_df.to_dict('records')]
        predicted_labels = [1 if row['Keyword Match'] or row['Fuzzy Match'] or row['Expected Data Match'] else 0 for row in results_df.to_dict('records')]

        # Calculate metrics - Might be used for different self developed bot
        accuracy = accuracy_score(actual_labels, predicted_labels)
        precision = precision_score(actual_labels, predicted_labels, zero_division=0)
        recall = recall_score(actual_labels, predicted_labels, zero_division=0)
        f1 = f1_score(actual_labels, predicted_labels, zero_division=0)

        # Prepare summary DataFrame
        summary_df = pd.DataFrame({
            "Metric": ["Accuracy", "Precision", "Recall", "F1-Score"],
            "Value": [accuracy, precision, recall, f1]
        })

        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            summary_df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        raise
