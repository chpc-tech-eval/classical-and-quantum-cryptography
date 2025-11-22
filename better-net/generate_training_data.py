# generate_training_data.py
#!/usr/bin/env python3
"""
Enhanced Realistic Password Training Data Generator
Generates more diverse and realistic password patterns
"""

import random
import string
import argparse
from datetime import datetime

# Expanded word lists for more realistic passwords
NOUNS = [
    'password', 'admin', 'user', 'login', 'secret', 'account', 'access', 
    'system', 'server', 'network', 'computer', 'email', 'phone', 'mobile',
    'home', 'office', 'work', 'school', 'company', 'business', 'security',
    'code', 'key', 'lock', 'safe', 'bank', 'money', 'pay', 'card', 'credit',
    'game', 'play', 'fun', 'music', 'movie', 'book', 'star', 'sun', 'moon',
    'dog', 'cat', 'bird', 'fish', 'horse', 'tiger', 'lion', 'bear', 'wolf',
    'car', 'bike', 'boat', 'plane', 'house', 'room', 'door', 'window', 'gate',
    'cloud', 'data', 'file', 'doc', 'photo', 'video', 'music', 'song', 'band',
    'friend', 'family', 'child', 'baby', 'boy', 'girl', 'man', 'woman',
    'summer', 'winter', 'spring', 'fall', 'day', 'night', 'time', 'date'
]

VERBS = [
    'love', 'like', 'need', 'want', 'have', 'make', 'take', 'give', 'get',
    'go', 'come', 'see', 'look', 'find', 'work', 'play', 'run', 'walk',
    'jump', 'swim', 'drive', 'fly', 'start', 'stop', 'change', 'set',
    'reset', 'enter', 'login', 'logout', 'access', 'open', 'close', 'lock',
    'create', 'delete', 'update', 'upload', 'download', 'share', 'send',
    'receive', 'call', 'text', 'message', 'post', 'upload', 'save'
]

ADJECTIVES = [
    'my', 'your', 'our', 'new', 'old', 'good', 'best', 'nice', 'cool',
    'hot', 'cold', 'big', 'small', 'fast', 'slow', 'strong', 'weak',
    'happy', 'sad', 'funny', 'serious', 'simple', 'easy', 'hard', 'safe',
    'secure', 'private', 'public', 'admin', 'super', 'mega', 'ultra',
    'red', 'blue', 'green', 'black', 'white', 'gold', 'silver', 'dark',
    'light', 'free', 'pro', 'lite', 'plus', 'max', 'mini', 'micro'
]

NAMES = [
    'john', 'jane', 'mike', 'sarah', 'david', 'lisa', 'chris', 'katie',
    'alex', 'emma', 'ryan', 'anna', 'tom', 'mary', 'james', 'linda',
    'robert', 'susan', 'michael', 'jennifer', 'william', 'patricia',
    'admin', 'user', 'test', 'demo', 'guest', 'root', 'superuser',
    'daniel', 'jessica', 'kevin', 'amanda', 'jason', 'michelle', 'steve',
    'andrew', 'emily', 'brian', 'nicole', 'justin', 'steven', 'rachel'
]

YEARS = ['2020', '2021', '2022', '2023', '2024', '2025', '1990', '1995', 
         '2000', '2005', '2010', '2015', '1985', '1975', '1980', '1999',
         '2026', '2027', '2028', '2029', '2030']

COMMON_SUFFIXES = ['123', '1234', '12345', '1', '12', '00', '01', '007', 
                   '111', '222', '333', '777', '999', '000', '69', '88',
                   '99', '100', '200', '500', '101', '202', '303', '404',
                   '505', '606', '707', '808', '909', '321', '654', '987']

SPECIAL_CHARS = ['!', '@', '#', '$', '&', '*', '_', '-', '.', '+', '=']

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
        # Two nouns
        lambda: random.choice(NOUNS) + random.choice(NOUNS),
        # Adjective + Verb
        lambda: random.choice(ADJECTIVES) + random.choice(VERBS),
    ]
    
    for _ in range(num_passwords):
        # Choose a pattern
        pattern = random.choice(patterns)
        base = pattern()
        
        # Apply common modifications
        modifications = []
        
        # Capitalization (30% chance)
        if random.random() < 0.3:
            if random.random() < 0.5:
                base = base.capitalize()
            else:
                # Random capitalization
                base = ''.join(c.upper() if random.random() < 0.3 else c for c in base)
        
        # Add numbers (70% chance)
        if random.random() < 0.7:
            if random.random() < 0.7:
                base += random.choice(COMMON_SUFFIXES)
            else:
                base += str(random.randint(1, 9999))
        
        # Add special character (25% chance)
        if random.random() < 0.25:
            pos = random.choice(['prefix', 'suffix', 'both'])
            if pos in ['prefix', 'both']:
                base = random.choice(SPECIAL_CHARS) + base
            if pos in ['suffix', 'both']:
                base += random.choice(SPECIAL_CHARS)
        
        # Leet speak substitution (20% chance)
        if random.random() < 0.2:
            leet_map = {
                'a': ['4', '@'],
                'e': ['3'],
                'i': ['1', '!'],
                'o': ['0'],
                's': ['5', '$'],
                't': ['7'],
                'l': ['1'],
                'b': ['8'],
                'g': ['9'],
            }
            leet_word = ''
            for char in base:
                if char.lower() in leet_map and random.random() < 0.5:
                    leet_word += random.choice(leet_map[char.lower()])
                else:
                    leet_word += char
            base = leet_word
        
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
            name + str(random.randint(1, 999)),
            name + random.choice(SPECIAL_CHARS),
            name + random.choice(YEARS),
            name + name,  # double name
            random.choice(SPECIAL_CHARS) + name,
            name.upper(),
        ]
        
        # Sometimes combine two names
        if random.random() < 0.2:
            name2 = random.choice(NAMES)
            variations.extend([
                name + name2,
                name.capitalize() + name2.capitalize(),
                name + "." + name2,
            ])
        
        password = random.choice(variations)
        passwords.add(password)
    
    return list(passwords)

def generate_year_based_passwords(num_passwords=200):
    """Generate passwords that include years"""
    passwords = set()
    
    common_bases = ['summer', 'winter', 'spring', 'fall', 'january', 'june',
                   'july', 'birthday', 'graduation', 'wedding', 'anniversary',
                   'password', 'admin', 'user', 'login', 'secret']
    
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
            base + "-" + year,
            year + "_" + base,
            base + random.choice(SPECIAL_CHARS) + year,
        ]
        
        password = random.choice(patterns)
        passwords.add(password)
    
    return list(passwords)

def generate_leet_speak_passwords(num_passwords=150):
    """Generate realistic leet speak passwords"""
    passwords = set()
    
    common_words = ['password', 'admin', 'secret', 'master', 'hello', 
                   'welcome', 'dragon', 'monkey', 'sunshine', 'princess',
                   'shadow', 'ninja', 'matrix', 'pizza', 'cookie', 'chocolate',
                   'silver', 'golden', 'summer', 'winter', 'autumn']
    
    leet_map = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
        'l': ['1'],
        'b': ['8'],
        'g': ['9'],
        'z': ['2'],
    }
    
    for _ in range(num_passwords):
        word = random.choice(common_words)
        leet_word = ''
        
        # Apply leet substitutions randomly
        for char in word:
            if char.lower() in leet_map and random.random() < 0.6:
                leet_word += random.choice(leet_map[char.lower()])
            else:
                leet_word += char
        
        # Common leet password patterns
        if random.random() < 0.4:
            leet_word = leet_word.capitalize()
        
        if random.random() < 0.7:
            leet_word += random.choice(['!', '123', '1', '!!', '1234', '00'])
        
        passwords.add(leet_word)
    
    return list(passwords)

def generate_phrase_passwords(num_passwords=100):
    """Generate passwords from short phrases"""
    passwords = set()
    
    phrases = [
        'letmein', 'trustno1', 'iloveyou', 'password1', 'hello123',
        'welcome1', 'sunshine', 'princess', 'football', 'baseball',
        'whatever', 'computer', 'internet', 'passw0rd', 'admin123',
        'qwerty123', 'abc123', '123abc', 'test123', 'demo123',
        'changeme', 'default', 'guest123', 'access123', 'login123'
    ]
    
    for _ in range(num_passwords):
        phrase = random.choice(phrases)
        
        # Apply common variations
        if random.random() < 0.4:
            phrase = phrase.capitalize()
        
        if random.random() < 0.5:
            phrase += random.choice(['!', '!!', '123', '1', '1234', '00'])
        
        # Sometimes add special chars
        if random.random() < 0.2:
            phrase = random.choice(SPECIAL_CHARS) + phrase
        
        passwords.add(phrase)
    
    return list(passwords)

def generate_keyboard_patterns(num_passwords=100):
    """Generate realistic keyboard patterns (not completely random)"""
    passwords = set()
    
    realistic_patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', '1qaz2wsx', '1q2w3e4r',
        'qazwsx', 'edcrfv', 'tgbnhy', 'yhnujm', 'zaq1xsw2', '!qaz@wsx',
        'qwer1234', 'asdf1234', 'zxcv1234', 'qweasdzxc', 'poiuyt', 'lkjhgf',
        'mnbvcx', '098765', '112233', 'aabbcc', 'qqqqqq', 'aaaaaa'
    ]
    
    for _ in range(num_passwords):
        pattern = random.choice(realistic_patterns)
        
        # Sometimes add minor variations
        if random.random() < 0.4:
            pattern += random.choice(['!', '123', '00', '1', '12'])
        
        if random.random() < 0.2:
            pattern = pattern.capitalize()
        
        passwords.add(pattern)
    
    return list(passwords)

def generate_random_mixed_passwords(num_passwords=200):
    """Generate passwords with random mixed patterns"""
    passwords = set()
    
    for _ in range(num_passwords):
        # Randomly combine different elements
        parts = []
        
        # Add 1-3 random elements
        num_parts = random.randint(1, 3)
        for _ in range(num_parts):
            element_type = random.choice(['word', 'number', 'special', 'name'])
            
            if element_type == 'word':
                parts.append(random.choice(NOUNS + VERBS + ADJECTIVES))
            elif element_type == 'number':
                parts.append(str(random.randint(0, 9999)))
            elif element_type == 'special':
                parts.append(random.choice(SPECIAL_CHARS))
            elif element_type == 'name':
                parts.append(random.choice(NAMES))
        
        password = ''.join(parts)
        
        # Apply random capitalization
        if random.random() < 0.3:
            password = password.capitalize()
        
        passwords.add(password)
    
    return list(passwords)

def main():
    parser = argparse.ArgumentParser(description='Generate realistic training passwords')
    parser.add_argument('--count', type=int, default=5000, help='Total number of passwords to generate')
    parser.add_argument('--output', type=str, default='passwords.txt', help='Output filename')
    parser.add_argument('--min-length', type=int, default=4, help='Minimum password length')
    parser.add_argument('--max-length', type=int, default=25, help='Maximum password length')
    
    args = parser.parse_args()
    
    print("Generating enhanced realistic training passwords...")
    
    # Generate different types of realistic passwords
    all_passwords = set()
    
    # Calculate distribution - focus on word-based patterns
    total = args.count
    word_based_count = int(total * 0.4)        # 40% word-based
    name_based_count = int(total * 0.15)       # 15% name-based  
    year_based_count = int(total * 0.1)        # 10% year-based
    leet_count = int(total * 0.1)              # 10% leet speak
    phrase_count = int(total * 0.1)            # 10% phrases
    keyboard_count = int(total * 0.05)         # 5% keyboard
    mixed_count = total - (word_based_count + name_based_count + 
                          year_based_count + leet_count + phrase_count + keyboard_count)  # 20% mixed
    
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
    
    print("  Generating mixed passwords...")
    all_passwords.update(generate_random_mixed_passwords(mixed_count))
    
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
    
    print(f"\n Generated {len(filtered_passwords)} realistic passwords")
    print(f" Average length: {avg_length:.1f} characters")
    print(f" Output file: {args.output}")
    print(f" Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show some examples
    print(f"\n Sample passwords:")
    for i, pwd in enumerate(filtered_passwords[:15]):
        print(f"  {i+1:2d}. {pwd}")

if __name__ == "__main__":
    main()
