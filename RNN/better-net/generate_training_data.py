#!/usr/bin/env python3
"""
Realistic Password Training Data Generator
Generates believable passwords based on real-world patterns
"""

import random
import string
import argparse
from datetime import datetime

# Common word lists for realistic passwords
NOUNS = [
    'password', 'admin', 'user', 'login', 'secret', 'account', 'access', 
    'system', 'server', 'network', 'computer', 'email', 'phone', 'mobile',
    'home', 'office', 'work', 'school', 'company', 'business', 'security',
    'code', 'key', 'lock', 'safe', 'bank', 'money', 'pay', 'card', 'credit',
    'game', 'play', 'fun', 'music', 'movie', 'book', 'star', 'sun', 'moon',
    'dog', 'cat', 'bird', 'fish', 'horse', 'tiger', 'lion', 'bear', 'wolf',
    'car', 'bike', 'boat', 'plane', 'house', 'room', 'door', 'window', 'gate'
]

VERBS = [
    'love', 'like', 'need', 'want', 'have', 'make', 'take', 'give', 'get',
    'go', 'come', 'see', 'look', 'find', 'work', 'play', 'run', 'walk',
    'jump', 'swim', 'drive', 'fly', 'start', 'stop', 'change', 'set',
    'reset', 'enter', 'login', 'logout', 'access', 'open', 'close', 'lock'
]

ADJECTIVES = [
    'my', 'your', 'our', 'new', 'old', 'good', 'best', 'nice', 'cool',
    'hot', 'cold', 'big', 'small', 'fast', 'slow', 'strong', 'weak',
    'happy', 'sad', 'funny', 'serious', 'simple', 'easy', 'hard', 'safe',
    'secure', 'private', 'public', 'admin', 'super', 'mega', 'ultra',
    'red', 'blue', 'green', 'black', 'white', 'gold', 'silver'
]

NAMES = [
    'john', 'jane', 'mike', 'sarah', 'david', 'lisa', 'chris', 'katie',
    'alex', 'emma', 'ryan', 'anna', 'tom', 'mary', 'james', 'linda',
    'robert', 'susan', 'michael', 'jennifer', 'william', 'patricia',
    'admin', 'user', 'test', 'demo', 'guest', 'root', 'superuser'
]

YEARS = ['2020', '2021', '2022', '2023', '2024', '2025', '1990', '1995', 
         '2000', '2005', '2010', '2015', '1985', '1975']

COMMON_SUFFIXES = ['123', '1234', '12345', '1', '12', '00', '01', '007', 
                   '111', '222', '333', '777', '999', '000', '69', '88']

SPECIAL_CHARS = ['!', '@', '#', '$', '&', '*']

def generate_word_based_passwords(num_passwords=500):
    """Generate passwords using real words and common patterns"""
    passwords = set()
    
    patterns = [
        # Adjective + Noun
        lambda: random.choice(ADJECTIVES) + random.choice(NOUNS),
        # Noun + Verb  
        lambda: random.choice(NOUNS) + random.choice(VERBS),
        # Verb + Noun
        lambda: random.choice(VERBS) + random.choice(NOUNS),
        # Name based
        lambda: random.choice(NAMES),
        # Single word
        lambda: random.choice(NOUNS + VERBS),
    ]
    
    for _ in range(num_passwords):
        # Choose a pattern
        pattern = random.choice(patterns)
        base = pattern()
        
        # Apply common modifications
        if random.random() < 0.3:
            # Capitalize first letter
            base = base.capitalize()
        
        if random.random() < 0.6:
            # Add numbers
            if random.random() < 0.7:
                base += random.choice(COMMON_SUFFIXES)
            else:
                base += str(random.randint(1, 999))
        
        if random.random() < 0.2:
            # Add special character
            base += random.choice(SPECIAL_CHARS)
        
        if random.random() < 0.15:
            # Leet speak substitution
            base = (base.replace('a', '@')
                       .replace('e', '3')
                       .replace('i', '1')
                       .replace('o', '0')
                       .replace('s', '5'))
        
        passwords.add(base)
    
    return list(passwords)

def generate_name_based_passwords(num_passwords=300):
    """Generate passwords based on names with common modifications"""
    passwords = set()
    
    for _ in range(num_passwords):
        name = random.choice(NAMES)
        
        # Various name-based patterns
        variations = [
            name,
            name.capitalize(),
            name + random.choice(COMMON_SUFFIXES),
            name + str(random.randint(1, 99)),
            name + random.choice(SPECIAL_CHARS),
            name + random.choice(YEARS),
        ]
        
        password = random.choice(variations)
        passwords.add(password)
    
    return list(passwords)

def generate_year_based_passwords(num_passwords=200):
    """Generate passwords that include years"""
    passwords = set()
    
    common_bases = ['summer', 'winter', 'spring', 'fall', 'january', 'june',
                   'july', 'birthday', 'graduation', 'wedding', 'anniversary']
    
    for _ in range(num_passwords):
        if random.random() < 0.5:
            base = random.choice(common_bases + NOUNS)
        else:
            base = random.choice(NAMES)
        
        year = random.choice(YEARS)
        
        # Different ordering patterns
        patterns = [
            base + year,
            year + base,
            base.capitalize() + year,
            base + "_" + year,
        ]
        
        password = random.choice(patterns)
        passwords.add(password)
    
    return list(passwords)

def generate_leet_speak_passwords(num_passwords=150):
    """Generate realistic leet speak passwords"""
    passwords = set()
    
    common_words = ['password', 'admin', 'secret', 'master', 'hello', 
                   'welcome', 'dragon', 'monkey', 'sunshine', 'princess']
    
    leet_map = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
    }
    
    for _ in range(num_passwords):
        word = random.choice(common_words)
        leet_word = ''
        
        # Apply leet substitutions randomly
        for char in word:
            if char.lower() in leet_map and random.random() < 0.4:
                leet_word += random.choice(leet_map[char.lower()])
            else:
                leet_word += char
        
        # Common leet password patterns
        if random.random() < 0.3:
            leet_word = leet_word.capitalize()
        
        if random.random() < 0.5:
            leet_word += random.choice(['!', '123', '1'])
        
        passwords.add(leet_word)
    
    return list(passwords)

def generate_phrase_passwords(num_passwords=100):
    """Generate passwords from short phrases"""
    passwords = set()
    
    phrases = [
        'letmein', 'trustno1', 'iloveyou', 'password1', 'hello123',
        'welcome1', 'sunshine', 'princess', 'football', 'baseball',
        'whatever', 'computer', 'internet', 'passw0rd', 'admin123'
    ]
    
    for _ in range(num_passwords):
        phrase = random.choice(phrases)
        
        # Apply common variations
        if random.random() < 0.3:
            phrase = phrase.capitalize()
        
        if random.random() < 0.4:
            phrase += random.choice(['!', '!!', '123', '1'])
        
        passwords.add(phrase)
    
    return list(passwords)

def generate_keyboard_patterns(num_passwords=100):
    """Generate realistic keyboard patterns (not completely random)"""
    passwords = set()
    
    realistic_patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', '1qaz2wsx', '1q2w3e4r',
        'qazwsx', 'edcrfv', 'tgbnhy', 'yhnujm', 'zaq1xsw2', '!qaz@wsx',
        'qwer1234', 'asdf1234', 'zxcv1234'
    ]
    
    for _ in range(num_passwords):
        pattern = random.choice(realistic_patterns)
        
        # Sometimes add minor variations
        if random.random() < 0.3:
            pattern += random.choice(['!', '123', '00'])
        
        passwords.add(pattern)
    
    return list(passwords)

def main():
    parser = argparse.ArgumentParser(description='Generate realistic training passwords')
    parser.add_argument('--count', type=int, default=2000, help='Total number of passwords to generate')
    parser.add_argument('--output', type=str, default='realistic_passwords.txt', help='Output filename')
    parser.add_argument('--min-length', type=int, default=4, help='Minimum password length')
    parser.add_argument('--max-length', type=int, default=20, help='Maximum password length')
    
    args = parser.parse_args()
    
    print("Generating realistic training passwords...")
    
    # Generate different types of realistic passwords
    all_passwords = set()
    
    # Calculate distribution - focus on word-based patterns
    total = args.count
    word_based_count = int(total * 0.5)        # 50% word-based
    name_based_count = int(total * 0.2)        # 20% name-based  
    year_based_count = int(total * 0.1)        # 10% year-based
    leet_count = int(total * 0.1)              # 10% leet speak
    phrase_count = int(total * 0.05)           # 5% phrases
    keyboard_count = total - (word_based_count + name_based_count + 
                            year_based_count + leet_count + phrase_count)  # 5% keyboard
    
    print("  Generating word-based passwords...")
    all_passwords.update(generate_word_based_passwords(word_based_count))
    
    print("  Generating name-based passwords...")
    all_passwords.update(generate_name_based_passwords(name_based_count))
    
    print("  Generating year-based passwords...")
    all_passwords.update(generate_year_based_passwords(year_based_count))
    
    print("  Generating leet speak passwords...")
    all_passwords.update(generate_leet_speak_passwords(leet_count))
    
    print("  Generating phrase passwords...")
    all_passwords.update(generate_phrase_passwords(phrase_count))
    
    print("  Generating keyboard patterns...")
    all_passwords.update(generate_keyboard_patterns(keyboard_count))
    
    # Filter by length and ensure uniqueness
    filtered_passwords = [
        pwd for pwd in all_passwords 
        if args.min_length <= len(pwd) <= args.max_length
    ]
    
    # Fill remaining slots with additional word-based passwords if needed
    while len(filtered_passwords) < args.count:
        additional = generate_word_based_passwords(args.count - len(filtered_passwords))
        for pwd in additional:
            if pwd not in filtered_passwords and args.min_length <= len(pwd) <= args.max_length:
                filtered_passwords.append(pwd)
                if len(filtered_passwords) >= args.count:
                    break
    
    # Trim to exact count and shuffle
    filtered_passwords = filtered_passwords[:args.count]
    random.shuffle(filtered_passwords)
    
    # Write to file
    with open(args.output, 'w', encoding='utf-8') as f:
        for password in filtered_passwords:
            f.write(password + '\n')
    
    # Statistics
    avg_length = sum(len(pwd) for pwd in filtered_passwords) / len(filtered_passwords)
    
    print(f"\n✅ Generated {len(filtered_passwords)} realistic passwords")
    print(f"📊 Average length: {avg_length:.1f} characters")
    print(f"💾 Output file: {args.output}")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show some examples
    print(f"\n🔍 Sample passwords:")
    for i, pwd in enumerate(filtered_passwords[:10]):
        print(f"  {i+1:2d}. {pwd}")

if __name__ == "__main__":
    main()
