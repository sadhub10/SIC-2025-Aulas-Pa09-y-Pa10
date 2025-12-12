import re
from typing import List, Dict

def extract_key_values(
    char_list: List[str],
    keywords: List[str],
    look_ahead: int = 6
    ) -> Dict[str, float]:
    """
    Extracts key-value pairs from a list of OCR/Vosk tokens, handling fuzzy 
    keyword matches and using a "Last-One-Wins" strategy for final amounts.
    """
    final_values: Dict[str, float] = {}

    # 1. Pre-process keywords for robust substring matching
    cleaned_keywords = {k.strip().upper(): k for k in keywords}

    # Regular expression for number validation
    number_pattern = re.compile(r'^\d*\.?\d+$')

    for i, item in enumerate(char_list):
        # Clean the current char item for matching (remove punctuation/spaces)
        cleaned_item = item.strip().upper().replace(':', '').replace('$', '').replace(' ', '')

        # 2. Robust Keyword Check (Substring Match)
        for clean_keyword, original_keyword in cleaned_keywords.items():
            if clean_keyword in cleaned_item:

                # 3. Search for the numerical value in the subsequent items.
                for j in range(i + 1, min(i + look_ahead, len(char_list))):
                    next_item = char_list[j].strip()

                    # Aggressively clean the potential value 
                    cleaned_value = re.sub(r'[^\d\.]', '', next_item.replace(',', '.'))

                    # Check if the cleaned item is a number
                    if number_pattern.match(cleaned_value):
                        try:
                            value = float(cleaned_value)

                            # LAST-ONE-WINS: Overwrite the dictionary entry
                            final_values[original_keyword] = value

                            # Break the inner loops and move to the next char item
                            break 
                        except ValueError:
                            continue

                # Stop checking other keywords against this single char item
                break

    return final_values
