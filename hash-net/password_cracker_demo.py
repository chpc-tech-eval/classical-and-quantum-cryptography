# password_cracker_demo.py
#!/usr/bin/env python3
"""
Password Cracker Demo
Allows users to input plaintext passwords, hash them, and attempt to crack them
"""

from improved_quantum_password_cracker import ImprovedQuantumPasswordCracker
from generate_training_data_with_hashes import ToyHasher
import time

class PasswordCrackerDemo:
    def __init__(self):
        self.hasher = ToyHasher()
        self.cracker = ImprovedQuantumPasswordCracker(self.hasher)
    
    def display_methods(self):
        """Display available cracking methods"""
        print("\nAvailable Cracking Methods:")
        print("1. Dictionary Attack (Fastest for common passwords)")
        print("2. Genetic Algorithm (Good for patterns)")
        print("3. QAOA-inspired Optimization (Quantum-inspired)")
        print("4. Brute Force (Slow but exhaustive)")
        print("5. All Methods (Comprehensive test)")
    
    def hash_password(self, password):
        """Hash a password and display the process"""
        print(f"\nHashing password: '{password}'")
        hash_val = self.hasher.hash_password(password)
        hash_hex = self.hasher.hash_to_hex(password)
        print(f"Hash (decimal): {hash_val}")
        print(f"Hash (hex): {hash_hex}")
        return hash_hex
    
    def run_cracking_method(self, method_name, target_hash, timeout=30):
        """Run a specific cracking method and return results"""
        print(f"\nRunning {method_name}...")
        start_time = time.time()
        
        if method_name == "Dictionary Attack":
            result = self.cracker.improved_dictionary_attack(target_hash, timeout=timeout)
        elif method_name == "Genetic Algorithm":
            result = self.cracker.improved_genetic_algorithm(target_hash, timeout=timeout)
        elif method_name == "QAOA-inspired Optimization":
            result = self.cracker.improved_qaoa_approach(target_hash, timeout=timeout)
        elif method_name == "Brute Force":
            result = self.cracker.improved_brute_force(target_hash, timeout=timeout)
        else:
            return None, 0, 0
        
        password_found, attempts, time_taken = result
        return password_found, attempts, time_taken
    
    def demo_single_password(self):
        """Demo cracking a single password"""
        print("\n" + "="*50)
        print("PASSWORD CRACKER DEMO")
        print("="*50)
        
        # Get password from user
        while True:
            password = input("\nEnter a password to hash and crack: ").strip()
            if password:
                break
            print("Please enter a valid password.")
        
        # Hash the password
        target_hash = self.hash_password(password)
        
        # Select method
        self.display_methods()
        
        while True:
            try:
                choice = input("\nSelect method (1-5): ").strip()
                if choice in ['1', '2', '3', '4', '5']:
                    break
                print("Please enter a number between 1 and 5.")
            except KeyboardInterrupt:
                return
        
        # Map choice to method
        method_map = {
            '1': ["Dictionary Attack"],
            '2': ["Genetic Algorithm"],
            '3': ["QAOA-inspired Optimization"],
            '4': ["Brute Force"],
            '5': ["Dictionary Attack", "Genetic Algorithm", "QAOA-inspired Optimization", "Brute Force"]
        }
        
        methods_to_run = method_map[choice]
        
        # Get timeout
        try:
            timeout = int(input(f"Enter timeout in seconds (default 30): ") or "30")
        except (ValueError, KeyboardInterrupt):
            timeout = 30
        
        print(f"\nStarting cracking process with {timeout} second timeout...")
        print("-" * 50)
        
        results = []
        
        for method in methods_to_run:
            password_found, attempts, time_taken = self.run_cracking_method(
                method, target_hash, timeout
            )
            
            success = password_found == password
            status = "SUCCESS" if success else "FAILED"
            
            if password_found and not success:
                status = "WRONG_PASSWORD"
            
            results.append({
                'method': method,
                'success': success,
                'password_found': password_found,
                'time': time_taken,
                'attempts': attempts,
                'status': status
            })
            
            # Display immediate result
            print(f"{method:25} : {status:15} | {time_taken:6.2f}s | {attempts:8} attempts")
            if password_found and password_found != password:
                print(f"  Found: '{password_found}' (incorrect)")
        
        # Display summary
        self.display_summary(results, password)
    
    def display_summary(self, results, original_password):
        """Display a summary of the cracking results"""
        print("\n" + "="*50)
        print("CRACKING SUMMARY")
        print("="*50)
        
        successful_methods = [r for r in results if r['success']]
        failed_methods = [r for r in results if not r['success']]
        
        print(f"Original password: '{original_password}'")
        print(f"Successful methods: {len(successful_methods)}/{len(results)}")
        
        if successful_methods:
            print("\nSuccessful Methods:")
            for result in successful_methods:
                print(f"  {result['method']:25} : {result['time']:6.2f}s, {result['attempts']} attempts")
        
        if failed_methods:
            print("\nFailed Methods:")
            for result in failed_methods:
                status_info = f" ({result['status']})" if result['status'] != "FAILED" else ""
                print(f"  {result['method']:25} : {result['time']:6.2f}s, {result['attempts']} attempts{status_info}")
        
        # Performance analysis
        if successful_methods:
            fastest = min(successful_methods, key=lambda x: x['time'])
            most_efficient = min(successful_methods, key=lambda x: x['attempts'])
            
            print(f"\nPerformance Analysis:")
            print(f"  Fastest method: {fastest['method']} ({fastest['time']:.2f}s)")
            print(f"  Most efficient: {most_efficient['method']} ({most_efficient['attempts']} attempts)")
    
    def batch_demo(self):
        """Demo with multiple pre-defined passwords using ALL methods"""
        print("\n" + "="*50)
        print("BATCH PASSWORD DEMO - ALL METHODS")
        print("="*50)
        
        test_passwords = [
            "password", "admin", "hello", "test123", 
            "secret", "123456", "letmein", "welcome", "securepass12", "crac", "paaaass"
        ]
        
        methods_to_test = [
            "Dictionary Attack",
            "Genetic Algorithm", 
            "QAOA-inspired Optimization",
            "Brute Force"
        ]
        
        print("Testing common passwords:")
        for i, pwd in enumerate(test_passwords, 1):
            print(f"  {i}. {pwd}")
        
        timeout = 5
        print(f"\nTesting {len(methods_to_test)} methods with {timeout} second timeout per method...")
        print("-" * 50)
        
        batch_results = []
        
        for password in test_passwords:
            print(f"\nCracking: '{password}'")
            target_hash = self.hasher.hash_to_hex(password)
            
            password_results = {'password': password, 'methods': {}}
            
            for method in methods_to_test:
                print(f"  {method:25}... ", end="", flush=True)
                
                password_found, attempts, time_taken = self.run_cracking_method(
                    method, target_hash, timeout=timeout
                )
                
                success = password_found == password
                status = "SUCCESS" if success else "FAILED"
                
                password_results['methods'][method] = {
                    'success': success,
                    'time': time_taken,
                    'attempts': attempts,
                    'password_found': password_found
                }
                
                print(f"{status} ({time_taken:.2f}s, {attempts} attempts)")
                
                if password_found and password_found != password:
                    print(f"    Found: '{password_found}' (incorrect)")
            
            batch_results.append(password_results)
        
        # Display comprehensive batch summary
        self.display_batch_summary(batch_results, methods_to_test)
    
    def display_batch_summary(self, batch_results, methods):
        """Display comprehensive batch results"""
        print("\n" + "="*60)
        print("COMPREHENSIVE BATCH SUMMARY")
        print("="*60)
        
        # Method performance statistics
        method_stats = {}
        for method in methods:
            method_stats[method] = {
                'success_count': 0,
                'total_time': 0,
                'total_attempts': 0,
                'success_passwords': []
            }
        
        # Calculate statistics
        for result in batch_results:
            password = result['password']
            for method, method_result in result['methods'].items():
                method_stats[method]['total_time'] += method_result['time']
                method_stats[method]['total_attempts'] += method_result['attempts']
                if method_result['success']:
                    method_stats[method]['success_count'] += 1
                    method_stats[method]['success_passwords'].append(password)
        
        # Display method performance
        print("\nMETHOD PERFORMANCE SUMMARY:")
        print("-" * 60)
        print(f"{'Method':25} {'Success':8} {'Avg Time':10} {'Avg Attempts':12} {'Success Rate':12}")
        print("-" * 60)
        
        for method, stats in method_stats.items():
            success_rate = (stats['success_count'] / len(batch_results)) * 100
            avg_time = stats['total_time'] / len(batch_results)
            avg_attempts = stats['total_attempts'] / len(batch_results)
            
            print(f"{method:25} {stats['success_count']:2}/{len(batch_results):2} {avg_time:9.2f}s {avg_attempts:11.0f} {success_rate:11.1f}%")
        
        # Password difficulty analysis
        print("\nPASSWORD DIFFICULTY ANALYSIS:")
        print("-" * 60)
        print(f"{'Password':12} {'Dict':6} {'Genetic':7} {'QAOA':6} {'Brute':6} {'Success Rate':12}")
        print("-" * 60)
        
        for result in batch_results:
            password = result['password']
            success_count = 0
            method_success = []
            
            for method in methods:
                success = result['methods'][method]['success']
                if success:
                    success_count += 1
                    method_success.append("✓")
                else:
                    method_success.append("✗")
            
            success_rate = (success_count / len(methods)) * 100
            print(f"{password:12} {method_success[0]:6} {method_success[1]:7} {method_success[2]:6} {method_success[3]:6} {success_rate:11.1f}%")
        
        # Overall statistics
        total_successful = sum(1 for result in batch_results 
                             if any(method['success'] for method in result['methods'].values()))
        
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total passwords tested: {len(batch_results)}")
        print(f"  Passwords cracked by at least one method: {total_successful}/{len(batch_results)}")
        print(f"  Overall success rate: {(total_successful/len(batch_results))*100:.1f}%")
        
        # Best performing method
        best_method = max(method_stats.items(), key=lambda x: x[1]['success_count'])
        print(f"  Best performing method: {best_method[0]} ({best_method[1]['success_count']}/{len(batch_results)} successes)")
    
    def run(self):
        """Main demo loop"""
        print("PASSWORD CRACKING DEMONSTRATION")
        print("This tool demonstrates password hashing and cracking techniques.")
        
        while True:
            print("\n" + "="*50)
            print("MAIN MENU")
            print("="*50)
            print("1. Crack a single password")
            print("2. Run batch demo (common passwords - ALL METHODS)")
            print("3. Exit")
            
            try:
                choice = input("\nSelect option (1-3): ").strip()
                
                if choice == '1':
                    self.demo_single_password()
                elif choice == '2':
                    self.batch_demo()
                elif choice == '3':
                    print("Exiting demo. Goodbye!")
                    break
                else:
                    print("Please enter 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\nExiting demo. Goodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    """Main function"""
    demo = PasswordCrackerDemo()
    demo.run()

if __name__ == "__main__":
    main()
