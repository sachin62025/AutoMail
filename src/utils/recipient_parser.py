# src/utils/recipient_parser.py

import pandas as pd
from typing import List, IO

def parse_from_text(text: str) -> List[str]:
    """Parses a comma-separated string of emails into a list."""
    if not text:
        return []
    return [email.strip() for email in text.split(",") if email.strip()]

def parse_from_csv(file: IO) -> List[str]:
    """Parses a CSV file for an 'Email' column and returns a list of emails."""
    try:
        df = pd.read_csv(file)
        if 'Email' in df.columns:
            # Drop any missing values and convert to a list
            return df['Email'].dropna().tolist()
        else:
            # Raise an error if the required column is missing
            raise ValueError("CSV file must have a column named 'Email'.")
    except Exception as e:
        # Re-raise with a more specific message for easier debugging
        raise ValueError(f"Error reading or parsing the CSV file: {e}")