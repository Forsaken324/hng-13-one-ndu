from collections import defaultdict
from model import String
import hashlib

def is_palindrome(text: str) -> bool:
    return text == text[::-1]

def chr_frequency_map(text: str) -> dict:
    freq_dict = defaultdict(int)
    for i in text:
        freq_dict[i] += 1
    return freq_dict

def word_count(text: str) -> int:
    text_cleaned = text.strip()
    return len(text_cleaned.split(' '))

def unique_characters(text: str) -> int:
    word_hash = {}
    unique_chr_count = 0
    for chr in text:
        if not chr in word_hash:
            unique_chr_count += 1
            word_hash[chr] = 0
    return unique_chr_count


def format_response(str_obj: String):
    response = {}
    response['id'] = str_obj.id
    response['value'] = str_obj.value
    
    properties_dict = {}
    
    properties_dict['length'] = str_obj.length
    properties_dict['is_palindrome'] = str_obj.is_palindrome
    properties_dict['unique_characters'] = str_obj.unique_characters
    properties_dict['word_count'] = str_obj.word_count
    properties_dict['sha256_hash'] = str_obj.sha256_hash
    properties_dict['character_frequency_map'] = chr_frequency_map(str_obj.value)
    
    response['properties'] = properties_dict
    response['created_at'] = str_obj.created_at.isoformat() + 'Z'
    
    return response

def hash_string(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()