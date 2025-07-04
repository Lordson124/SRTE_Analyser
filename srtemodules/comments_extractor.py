import pandas as pd
import numpy as np
import re
from collections import Counter
from textblob import TextBlob # New import for sentiment analysis

# List of common "empty" comment indicators (case-insensitive)
EMPTY_COMMENT_PATTERNS = re.compile(
    r'^(nan|nil|none|nothing|nill|n/a|n/c|noting else|nun)$',
    re.IGNORECASE
)

def _clean_single_comment(comment_text):
    """Helper function to clean a single comment string."""
    if pd.isna(comment_text):
        return ''
    
    comment_text = str(comment_text).strip() # Ensure it's a string and strip whitespace

    # If the comment is just a number (e.g., '0', '1', '2'), treat as empty
    if comment_text.isdigit():
        return ''

    # Remove hyphens, numbers followed by a period and space (e.g., "1. "),
    # and various punctuation marks.
    comment_text = re.sub(r'\-|\d\.\s|[.?_!*]+', '', comment_text)
    
    # Replace common "empty" words/phrases (case-insensitive)
    if EMPTY_COMMENT_PATTERNS.match(comment_text):
        return ''

    return comment_text.strip() # Strip again after regex operations

def get_comments(df, columns):
    """
    Extracts and cleans comments from specified DataFrame columns.
    Handles multiple columns by concatenating them.
    """
    comments = []
    for col in columns:
        # Apply the cleaner function to each cell in the column
        df.loc[:, col] = df[col].apply(_clean_single_comment)
        comments.extend(df[col].tolist()) # Add all cleaned comments to the list

    # Filter out any remaining empty strings that might result from cleaning
    return [c for c in comments if c]

def get_series(series):
    """
    Extracts and cleans comments from a single Pandas Series.
    """
    # Apply the cleaner function to each cell in the series
    cleaned_series = series.apply(_clean_single_comment)
    
    # Filter out any remaining empty strings
    return [c for c in cleaned_series.tolist() if c]


def cleanup(x):
    """
    Flattens a list of lists into a single list, removes empty strings.
    This version is for processing comments before aggregation, so it
    does NOT make unique or sort.
    """
    # x is already a list of strings from get_comments or get_series
    # No need to flatten list of lists here, just filter empty strings
    return [item for item in x if item]

def cleanitup(x):
    """
    Flattens a list of lists, removes empty strings, strips whitespace.
    Crucially, this version does NOT capitalize to preserve original casing.
    This is used for saving to text files, where capitalization might be desired
    but for aggregation, we want original casing.
    """
    g = []
    for i in x:
        for r in i:
            if r != '':
                g.append(str(r).strip()) # Only strip, no capitalize
    return g

def analyze_sentiment(text, polarity_override=None): # Added polarity_override for average sentiment
    """
    Analyzes the sentiment of a given text or uses an override polarity.
    Returns a tuple: (polarity, sentiment_category)
    Polarity: -1.0 (negative) to +1.0 (positive)
    Sentiment_category: 'Positive', 'Negative', 'Neutral'
    """
    if polarity_override is not None:
        polarity = polarity_override
    else:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

    if polarity > 0.1: # Slightly positive threshold
        category = 'Positive'
    elif polarity < -0.1: # Slightly negative threshold
        category = 'Negative'
    else:
        category = 'Neutral'
    return polarity, category

def get_aggregated_comments_with_sentiment(comment_list):
    """
    Aggregates similar comments, counts their occurrences, and formats them,
    including sentiment analysis.
    Returns a list of (formatted_comment_string, polarity, category) tuples.
    """
    # Dictionary to store counts, original comment text, and sentiment
    # Key: normalized comment (lowercase, stripped)
    # Value: [count, original_comment_text, total_polarity, num_comments_for_avg_polarity]
    aggregated = {}

    for comment in comment_list:
        normalized_comment = comment.lower()
        polarity, _ = analyze_sentiment(comment) # Get sentiment for each individual comment

        if normalized_comment in aggregated:
            aggregated[normalized_comment][0] += 1
            aggregated[normalized_comment][2] += polarity # Sum polarities for average
            aggregated[normalized_comment][3] += 1
        else:
            aggregated[normalized_comment] = [1, comment, polarity, 1]

    # Convert to a list of (original_comment, count, avg_polarity, avg_category) tuples
    # Sort by count (descending), then by original comment text (alphabetical, case-insensitive)
    sorted_comments_with_sentiment = []
    for k, v in aggregated.items():
        count, original_text, total_polarity, num_comments = v
        avg_polarity = total_polarity / num_comments
        _, avg_category = analyze_sentiment(original_text, avg_polarity) # Use avg_polarity to get category
        sorted_comments_with_sentiment.append((original_text, count, avg_polarity, avg_category))

    sorted_comments_with_sentiment = sorted(
        sorted_comments_with_sentiment,
        key=lambda item: (-item[1], item[0].lower()) # Sort by count desc, then text asc
    )

    # Format for display: "Comment (xN) - Sentiment"
    formatted_output = []
    for comment_text, count, _, category in sorted_comments_with_sentiment:
        if count > 1:
            formatted_output.append(f"{comment_text} (x{count}) - {category}")
        else:
            formatted_output.append(f"{comment_text} - {category}")
            
    return formatted_output, [s[2] for s in sorted_comments_with_sentiment] # Return formatted comments and list of polarities

def extract_series(df, name):
    """Extracts comments from a DataFrame series and saves them to a text file."""
    np.savetxt(f'./Comments/{name}.txt', cleanitup(get_series(df)), fmt='%s', delimiter='\n')
    print(f'Comments for {name} successfully extracted...')
     
def extract_df(df, name, col):
    """Extracts comments from DataFrame columns and saves them to a text file."""
    np.savetxt(f'./Comments/{name}.txt', cleanitup(get_comments(df, col)), fmt='%s', delimiter='\n')
    print(f'Comments for {name} successfully extracted...')

def extract_likes(df, filter_course):
    """Extracts 'likes' comments for a filtered course and aggregates them with sentiment."""
    likes_column = df.columns[2]
    cleaned_comments = get_comments(filter_course.copy(), [likes_column])
    return get_aggregated_comments_with_sentiment(cleaned_comments)

def extract_dislikes(df, filter_course):
    """Extracts 'dislikes' comments for a filtered course and aggregates them with sentiment."""
    dislikes_column = df.columns[3]
    cleaned_comments = get_comments(filter_course.copy(), [dislikes_column])
    return get_aggregated_comments_with_sentiment(cleaned_comments)
