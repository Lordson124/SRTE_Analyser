import pandas as pd
import numpy as np
import re
from collections import Counter # New import for counting

# List of common "empty" comment indicators (case-insensitive)
# This will be used to filter out non-meaningful comments
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
    # This prevents integers from being passed as comments
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
        # Use .loc for explicit assignment to avoid SettingWithCopyWarning
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

def get_aggregated_comments(comment_list):
    """
    Aggregates similar comments, counts their occurrences, and formats them.
    Preserves original casing for display, but aggregates case-insensitively.
    """
    # Dictionary to store counts and a canonical (first seen) version of each comment
    # Key: normalized comment (lowercase, stripped)
    # Value: [count, original_comment_text]
    aggregated = {}

    for comment in comment_list:
        # Normalize for counting (case-insensitive comparison)
        normalized_comment = comment.lower() 
        if normalized_comment in aggregated:
            aggregated[normalized_comment][0] += 1
        else:
            # Store count and the original comment text (preserving casing)
            aggregated[normalized_comment] = [1, comment] 

    # Convert to a list of (original_comment, count) tuples
    # Sort by count (descending), then by original comment text (alphabetical, case-insensitive)
    sorted_comments = sorted(
        [ (v[1], v[0]) for k, v in aggregated.items() ],
        key=lambda item: (-item[1], item[0].lower()) 
    )

    # Format for display: "Comment (xN)" or "Comment"
    formatted_comments = []
    for comment_text, count in sorted_comments:
        if count > 1:
            formatted_comments.append(f"{comment_text} (x{count})")
        else:
            formatted_comments.append(comment_text)
    return formatted_comments


def extract_series(df, name):
    """Extracts comments from a DataFrame series and saves them to a text file."""
    # Note: cleanitup is used here, which does not capitalize.
    np.savetxt(f'./Comments/{name}.txt', cleanitup(get_series(df)), fmt='%s', delimiter='\n')
    print(f'Comments for {name} successfully extracted...')
     
def extract_df(df, name, col):
    """Extracts comments from DataFrame columns and saves them to a text file."""
    # Note: cleanitup is used here, which does not capitalize.
    np.savetxt(f'./Comments/{name}.txt', cleanitup(get_comments(df, col)), fmt='%s', delimiter='\n')
    print(f'Comments for {name} successfully extracted...')

def extract_likes(df, filter_course):
    """Extracts 'likes' comments for a filtered course and aggregates them."""
    likes_column = df.columns[2] # Assumes 'Course likes' is at index 2
    # Pass a copy to avoid SettingWithCopyWarning
    cleaned_comments = get_comments(filter_course.copy(), [likes_column]) 
    return get_aggregated_comments(cleaned_comments)

def extract_dislikes(df, filter_course):
    """Extracts 'dislikes' comments for a filtered course and aggregates them."""
    dislikes_column = df.columns[3] # Assumes 'Course dislikes' is at index 3
    # Pass a copy to avoid SettingWithCopyWarning
    cleaned_comments = get_comments(filter_course.copy(), [dislikes_column]) 
    return get_aggregated_comments(cleaned_comments)

