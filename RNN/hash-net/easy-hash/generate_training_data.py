#!/usr/bin/env python3
"""
Password Training Data Generator
Generates realistic passwords for training neural networks
"""

import random
import string
import argparse
from datetime import datetime

def generate_common_patterns(num_passwords=1000):
    """Generate passwords based on common patterns"""
    passwords = set()
    
    # Common base words and patterns
    base_words = ['password', 'admin', 'user', 'login', 'secret', 'qwerty', 
                  'letmein', 'welcome', 'monkey', 'dragon', 'master', 'hello',
                  'freedom', 'whatever', 'computer', 'internet', 'sunshine',
                  'princess', 'superman', 'baseball', 'football', 'mustang']
    
    common_suffixes = ['123', '1234', '12345', '123456', '1', '12', '!', '!!', 
                       '!@#', '@', '#', '000', '007', '111', '777', '999']
    
    common_prefixes = ['my', 'new', 'super', 'ilove', 'the', 'a']
    
    years = ['2020', '2021', '2022', '2023', '2024', '2025', '1990', '1995', 
             '2000', '2005', '2010', '2015']
    
    # Generate pattern-based passwords
    for _ in range(num_passwords // 2):
        # Word + numbers
        if random.random() < 0.7:
            base = random.choice(base_words)
            suffix = random.choice(common_suffixes + years)
            password = base + suffix
            passwords.add(password)
        
        # Prefix + word + numbers
        if random.random() < 0.3:
            prefix = random.choice(common_prefixes)
            base = random.choice(base_words)
            suffix = random.choice(common_suffixes)
            password = prefix + base + suffix
            passwords.add(password)
        
        # Word with character substitutions
        if random.random() < 0.2:
            base = random.choice(base_words)
            subbed = base.replace('a', '@').replace('s', '$').replace('o', '0').replace('i', '1')
            if random.random() < 0.5:
                subbed += random.choice(common_suffixes)
            passwords.add(subbed)
    
    return list(passwords)

def generate_random_passwords(num_passwords=500):
    """Generate completely random passwords"""
    passwords = set()
    
    for _ in range(num_passwords):
        length = random.randint(6, 20)
        
        # Mix of character types
        if random.random() < 0.3:
            # Alphanumeric only
            chars = string.ascii_letters + string.digits
        elif random.random() < 0.5:
            # With special characters
            chars = string.ascii_letters + string.digits + "!@#$%&*"
        else:
            # Letters only
            chars = string.ascii_letters
        
        password = ''.join(random.choice(chars) for _ in range(length))
        passwords.add(password)
    
    return list(passwords)

def generate_keyboard_patterns(num_passwords=200):
    """Generate keyboard pattern passwords"""
    passwords = set()
    
    # Common keyboard patterns
    keyboard_rows = [
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
        '1234567890', '!@#$%^&*()'
    ]
    
    patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', '!@#$%^',
        'qazwsx', 'edcrfv', 'tgbnhy', 'yhnujm', '1qaz2wsx',
        '1q2w3e4r', '1qa2ws3ed', 'zaq1xsw2', '!qaz@wsx'
    ]
    
    for _ in range(num_passwords):
        if random.random() < 0.6:
            # Use existing patterns
            base = random.choice(patterns)
        else:
            # Generate new patterns
            row = random.choice(keyboard_rows)
            start = random.randint(0, len(row) - 4)
            length = random.randint(4, 8)
            base = row[start:start + length]
        
        # Sometimes add numbers/special chars
        if random.random() < 0.4:
            base += random.choice(['123', '1234', '!', '!!', '000'])
        
        passwords.add(base)
    
    return list(passwords)

def generate_leet_speak_passwords(num_passwords=150):
    """Generate leet speak passwords"""
    passwords = set()
    
    common_words = ['password', 'admin', 'secret', 'hacker', 'master', 
                    'hello', 'test', 'demo', 'access', 'security']
    
    leet_map = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
        'b': ['8'],
        'g': ['9']
    }
    
    for _ in range(num_passwords):
        word = random.choice(common_words)
        leet_word = ''
        
        for char in word:
            if char.lower() in leet_map and random.random() < 0.6:
                leet_word += random.choice(leet_map[char.lower()])
            else:
                leet_word += char
        
        # Sometimes capitalize or add suffixes
        if random.random() < 0.3:
            leet_word = leet_word.capitalize()
        
        if random.random() < 0.5:
            leet_word += random.choice(['!', '123', '1', '007'])
        
        passwords.add(leet_word)
    
    return list(passwords)

def generate_phrase_based_passwords(num_passwords=100):
    """Generate passwords based on phrases"""
    passwords = set()
    
    phrases = [
        'iloveyou', 'trustno1', 'letmein', 'passw0rd', 'sunshine',
        'princess', 'football', 'baseball', 'welcome', 'master',
        'hello', 'freedom', 'whatever', 'computer', 'internet'
    ]
    
    for _ in range(num_passwords):
        phrase = random.choice(phrases)
        
        # Various transformations
        if random.random() < 0.3:
            # Capitalize first letter
            phrase = phrase.capitalize()
        
        if random.random() < 0.4:
            # Add numbers
            phrase += str(random.randint(0, 999))
        
        if random.random() < 0.2:
            # Add special characters
            phrase += random.choice(['!', '@', '#', '$'])
        
        passwords.add(phrase)
    
    return list(passwords)

def main():
    parser = argparse.ArgumentParser(description='Generate training passwords for neural networks')
    parser.add_argument('--count', type=int, default=2000, help='Total number of passwords to generate')
    parser.add_argument('--output', type=str, default='training_passwords.txt', help='Output filename')
    parser.add_argument('--min-length', type=int, default=4, help='Minimum password length')
    parser.add_argument('--max-length', type=int, default=30, help='Maximum password length')
    
    args = parser.parse_args()
    
    print("Generating training passwords...")
    
    # Generate different types of passwords
    all_passwords = set()
    
    # Calculate distribution
    total = args.count
    common_count = int(total * 0.4)
    random_count = int(total * 0.3)
    keyboard_count = int(total * 0.15)
    leet_count = int(total * 0.1)
    phrase_count = total - common_count - random_count - keyboard_count - leet_count
    
    # Generate each type
    print("  Generating common patterns...")
    all_passwords.update(generate_common_patterns(common_count))
    
    print("  Generating random passwords...")
    all_passwords.update(generate_random_passwords(random_count))
    
    print("  Generating keyboard patterns...")
    all_passwords.update(generate_keyboard_patterns(keyboard_count))
    
    print("  Generating leet speak passwords...")
    all_passwords.update(generate_leet_speak_passwords(leet_count))
    
    print("  Generating phrase-based passwords...")
    all_passwords.update(generate_phrase_based_passwords(phrase_count))
    
    # Filter by length
    filtered_passwords = [
        pwd for pwd in all_passwords 
        if args.min_length <= len(pwd) <= args.max_length
    ]
    
    # Ensure we have the requested count
    while len(filtered_passwords) < args.count:
        additional = generate_random_passwords(args.count - len(filtered_passwords))
        filtered_passwords.extend([p for p in additional if p not in filtered_passwords])
    
    # Trim to exact count
    filtered_passwords = filtered_passwords[:args.count]
    
    # Shuffle
    random.shuffle(filtered_passwords)
    
    # Write to file
    with open(args.output, 'w', encoding='utf-8') as f:
        for password in filtered_passwords:
            f.write(password + '\n')
    
    # Statistics
    avg_length = sum(len(pwd) for pwd in filtered_passwords) / len(filtered_passwords)
    
    print(f"\nGenerated {len(filtered_passwords)} passwords")
    print(f"Average length: {avg_length:.1f} characters")
    print(f"Output file: {args.output}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
