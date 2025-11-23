# reset_and_test.py
from simple_hash import SimpleHashFunction

def test_simple_hash():
    hash_fn = SimpleHashFunction()
    
    test_passwords = ["test123", "hello123", "password123"]
    
    print("Testing Simple Hash Function:")
    print("=" * 30)
    
    for pwd in test_passwords:
        hash_val = hash_fn.actual_hash(pwd)
        print(f"'{pwd}' -> hash: {hash_val}")
    
    print("\nThe hash should be trivial to invert now!")

if __name__ == "__main__":
    test_simple_hash()
