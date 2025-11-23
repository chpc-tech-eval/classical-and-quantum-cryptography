# enhanced_password_cracker_demo.py
#!/usr/bin/env python3
"""
Enhanced Password Cracker Demo with Comprehensive Analytics
"""

from improved_quantum_password_cracker_comprehensive import *
import time
import json

class EnhancedPasswordCrackerDemo:
    def __init__(self):
        self.security_level = SecurityLevel.MEDIUM
        self.complexity = PasswordComplexity.ALPHANUMERIC_MIXED
        self.cracker = None
        self.initialize_cracker()
    
    def initialize_cracker(self):
        """Initialize the cracker with current settings"""
        self.cracker = ComprehensivePasswordCracker(
            security_level=self.security_level,
            complexity=self.complexity,
            verbose=True
        )
    
    def display_security_levels(self):
        """Display available security levels"""
        print("\nAvailable Security Levels:")
        for i, level in enumerate(SecurityLevel, 1):
            bits = level.value
            print(f"{i}. {level.name} ({bits}-bit security)")
    
    def display_complexity_levels(self):
        """Display password complexity levels"""
        print("\nAvailable Complexity Levels:")
        for i, comp in enumerate(PasswordComplexity, 1):
            print(f"{i}. {comp.name}")
            print(f"   Charset: {comp.value[:50]}{'...' if len(comp.value) > 50 else ''}")
    
    def configure_settings(self):
        """Configure cracker settings"""
        print("\nCONFIGURATION MENU")
        print("=" * 40)
        
        while True:
            print(f"\nCurrent Settings:")
            print(f"  Security Level: {self.security_level.name}")
            print(f"  Complexity: {self.complexity.name}")
            print(f"  Charset Size: {len(self.complexity.value)} characters")
            
            print("\nOptions:")
            print("1. Change Security Level")
            print("2. Change Complexity Level")
            print("3. Return to Main Menu")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                self.display_security_levels()
                try:
                    level_choice = int(input("Select security level (1-4): "))
                    if 1 <= level_choice <= 4:
                        self.security_level = list(SecurityLevel)[level_choice - 1]
                        self.initialize_cracker()
                        print(f"Security level set to {self.security_level.name}")
                    else:
                        print("Invalid choice")
                except ValueError:
                    print("Please enter a number")
            
            elif choice == '2':
                self.display_complexity_levels()
                try:
                    comp_choice = int(input("Select complexity level (1-4): "))
                    if 1 <= comp_choice <= 4:
                        self.complexity = list(PasswordComplexity)[comp_choice - 1]
                        self.initialize_cracker()
                        print(f"Complexity level set to {self.complexity.name}")
                    else:
                        print("Invalid choice")
                except ValueError:
                    print("Please enter a number")
            
            elif choice == '3':
                break
            else:
                print("Invalid option")
    
    def demo_single_password(self):
        """Demo cracking a single password"""
        print("\n" + "=" * 50)
        print("SINGLE PASSWORD CRACKING DEMO")
        print("=" * 50)
        
        # Get password from user
        while True:
            password = input("\nEnter a password to hash and crack: ").strip()
            if password:
                break
            print("Please enter a valid password.")
        
        # Hash the password
        target_hash = self.cracker.hasher.hash_to_hex(password)
        print(f"\nPassword: '{password}'")
        print(f"Hash ({self.security_level.value}-bit): {target_hash}")
        print(f"Charset: {self.complexity.value[:30]}...")
        
        # Select methods
        methods = ["dictionary", "genetic", "quantum", "hybrid"]
        
        print(f"\nAvailable Methods:")
        for i, method in enumerate(methods, 1):
            print(f"{i}. {method}")
        print("5. All Methods (Comprehensive Test)")
        
        while True:
            try:
                choice = input("\nSelect method (1-5): ").strip()
                if choice in ['1', '2', '3', '4', '5']:
                    break
                print("Please enter a number between 1 and 5.")
            except KeyboardInterrupt:
                return
        
        # Map choice to methods
        method_map = {
            '1': ["dictionary"],
            '2': ["genetic"], 
            '3': ["quantum"],
            '4': ["hybrid"],
            '5': ["dictionary", "genetic", "quantum", "hybrid"]
        }
        
        methods_to_run = method_map[choice]
        
        # Get timeout
        try:
            timeout = int(input(f"Enter timeout per method in seconds (default 30): ") or "30")
        except (ValueError, KeyboardInterrupt):
            timeout = 30
        
        print(f"\nStarting cracking process...")
        print(f"Security: {self.security_level.name}, Timeout: {timeout}s")
        print("-" * 60)
        
        # Run attacks
        results = self.cracker.comprehensive_attack(target_hash, methods_to_run, timeout)
        
        # Display results
        self.display_single_results(results, password)
    
    def display_single_results(self, results: Dict[str, CrackResult], original_password: str):
        """Display results for single password cracking"""
        print("\n" + "=" * 60)
        print("CRACKING RESULTS")
        print("=" * 60)
        
        print(f"Original password: '{original_password}'")
        print(f"Security level: {self.security_level.name}")
        print(f"Complexity: {self.complexity.name}")
        print()
        
        successful_methods = []
        failed_methods = []
        
        for method, result in results.items():
            status = "SUCCESS" if result.success else "FAILED"
            if result.success:
                successful_methods.append((method, result))
            else:
                failed_methods.append((method, result))
            
            print(f"{method:15} : {status:8} | {result.time_taken:6.2f}s | "
                  f"{result.attempts:8} attempts")
            
            if result.password and result.password != original_password:
                print(f"                 Found: '{result.password}' (WRONG)")
        
        # Summary
        print(f"\nSUMMARY: {len(successful_methods)}/{len(results)} methods successful")
        
        if successful_methods:
            print("\nSuccessful Methods:")
            for method, result in successful_methods:
                print(f"  {method:15} : {result.time_taken:6.2f}s, {result.attempts} attempts")
        
        # Performance analysis
        if successful_methods:
            fastest = min(successful_methods, key=lambda x: x[1].time_taken)
            most_efficient = min(successful_methods, key=lambda x: x[1].attempts)
            
            print(f"\nPerformance Analysis:")
            print(f"  Fastest method: {fastest[0]} ({fastest[1].time_taken:.2f}s)")
            print(f"  Most efficient: {most_efficient[0]} ({most_efficient[1].attempts} attempts)")
    
    def batch_performance_test(self):
        """Run comprehensive batch performance test"""
        print("\n" + "=" * 50)
        print("COMPREHENSIVE BATCH PERFORMANCE TEST")
        print("=" * 50)
        
        # Test passwords of varying complexity
        test_passwords = [
            # Simple passwords
            "a", "ab", "abc", "test", "pass", "1234", "pas",
            # Common passwords  
            "password", "admin", "hello", "secret", "123456", "13579",
            # Moderate complexity
            "Password123", "Admin2024", "HelloWorld", "Test123!", "PW0RD"
            # High complexity (previously problematic)
            "securepass12", "crac", "paaaass", "MySecurePass123!",
            "Quantum2024", "Test@123", "hello_world", "difficultpass"
        ]
        
        methods = ["dictionary", "genetic", "quantum", "hybrid"]
        timeout = 20  # Reduced timeout for batch testing
        
        print(f"Testing {len(test_passwords)} passwords with {len(methods)} methods")
        print(f"Timeout: {timeout}s per method, Security: {self.security_level.name}")
        print("-" * 60)
        
        batch_results = []
        
        for i, password in enumerate(test_passwords, 1):
            print(f"\n[{i:2d}/{len(test_passwords)}] Cracking: '{password}'")
            target_hash = self.cracker.hasher.hash_to_hex(password)
            
            password_results = {'password': password, 'methods': {}}
            
            for method in methods:
                start_time = time.time()
                
                if method == "dictionary":
                    result = self.cracker.enhanced_dictionary_attack(target_hash, timeout)
                elif method == "genetic":
                    result = self.cracker.adaptive_genetic_algorithm(target_hash, timeout=timeout)
                elif method == "quantum":
                    result = self.cracker.quantum_inspired_search(target_hash, timeout=timeout)
                elif method == "hybrid":
                    result = self.cracker.hybrid_attack(target_hash, timeout=timeout)
                
                password_results['methods'][method] = {
                    'success': result.success,
                    'time': result.time_taken,
                    'attempts': result.attempts,
                    'password_found': result.password
                }
                
                status = "✓" if result.success else "✗"
                print(f"  {method:12} {status} {result.time_taken:5.2f}s {result.attempts:6} attempts")
                
                # Record for statistics
                self.cracker.stats.record_attack(result, password)
            
            batch_results.append(password_results)
        
        # Generate comprehensive analysis
        self.display_batch_analysis(batch_results, methods)
        
        # Export results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"batch_results_{timestamp}.json"
        self.cracker.stats.export_results(filename)
        
        # Generate plots
        plot_filename = f"performance_plot_{timestamp}.png"
        self.cracker.stats.plot_performance(plot_filename)
    
    def display_batch_analysis(self, batch_results, methods):
        """Display comprehensive batch analysis"""
        print("\n" + "=" * 70)
        print("COMPREHENSIVE BATCH ANALYSIS")
        print("=" * 70)
        
        # Method statistics
        method_stats = {}
        for method in methods:
            method_stats[method] = {
                'success_count': 0,
                'total_time': 0,
                'total_attempts': 0,
                'success_passwords': []
            }
        
        # Password statistics
        password_stats = {}
        
        for result in batch_results:
            password = result['password']
            password_stats[password] = {
                'length': len(password),
                'complexity': self.cracker.stats.calculate_complexity(password),
                'success_count': 0,
                'methods_successful': []
            }
            
            for method in methods:
                method_result = result['methods'][method]
                method_stats[method]['total_time'] += method_result['time']
                method_stats[method]['total_attempts'] += method_result['attempts']
                
                if method_result['success']:
                    method_stats[method]['success_count'] += 1
                    method_stats[method]['success_passwords'].append(password)
                    password_stats[password]['success_count'] += 1
                    password_stats[password]['methods_successful'].append(method)
        
        # Display method performance
        print("\nMETHOD PERFORMANCE SUMMARY:")
        print("-" * 70)
        print(f"{'Method':12} {'Success':8} {'Avg Time':10} {'Avg Attempts':14} {'Success Rate':12}")
        print("-" * 70)
        
        for method, stats in method_stats.items():
            success_rate = (stats['success_count'] / len(batch_results)) * 100
            avg_time = stats['total_time'] / len(batch_results)
            avg_attempts = stats['total_attempts'] / len(batch_results)
            
            print(f"{method:12} {stats['success_count']:2d}/{len(batch_results):2d} "
                  f"{avg_time:9.2f}s {avg_attempts:13.0f} {success_rate:11.1f}%")
        
        # Password difficulty analysis
        print("\nPASSWORD DIFFICULTY ANALYSIS:")
        print("-" * 70)
        print(f"{'Password':20} {'Len':3} {'Complexity':10} {'Dict':4} {'Gen':4} {'Qnt':4} {'Hyb':4} {'Success':8}")
        print("-" * 70)
        
        for password, stats in password_stats.items():
            method_success = []
            for method in methods:
                method_success.append("✓" if method in stats['methods_successful'] else "✗")
            
            success_rate = (stats['success_count'] / len(methods)) * 100
            
            print(f"{password:20} {stats['length']:3d} {stats['complexity']:10.0f} "
                  f"{method_success[0]:4} {method_success[1]:4} {method_success[2]:4} "
                  f"{method_success[3]:4} {success_rate:7.1f}%")
        
        # Overall statistics
        total_successful = sum(1 for stats in password_stats.values() 
                             if stats['success_count'] > 0)
        
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total passwords tested: {len(batch_results)}")
        print(f"  Passwords cracked by at least one method: {total_successful}/{len(batch_results)}")
        print(f"  Overall success rate: {(total_successful/len(batch_results))*100:.1f}%")
        
        # Best performing method
        best_method = max(method_stats.items(), key=lambda x: x[1]['success_count'])
        print(f"  Best performing method: {best_method[0]} "
              f"({best_method[1]['success_count']}/{len(batch_results)} successes)")
        
        # Most difficult password
        most_difficult = min(password_stats.items(), 
                           key=lambda x: x[1]['success_count'])
        print(f"  Most difficult password: '{most_difficult[0]}' "
              f"({most_difficult[1]['success_count']}/{len(methods)} methods)")
    
    def run(self):
        """Main demo loop"""
        print("ENHANCED QUANTUM PASSWORD CRACKER DEMONSTRATION")
        print("Academic Research Tool - Toy Hashing Algorithm Only")
        print("=" * 60)
        
        while True:
            print("\n" + "=" * 50)
            print("MAIN MENU")
            print("=" * 50)
            print("1. Configure Settings (Security Level & Complexity)")
            print("2. Crack Single Password")
            print("3. Comprehensive Batch Test")
            print("4. Generate Performance Reports")
            print("5. Exit")
            
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    self.configure_settings()
                elif choice == '2':
                    self.demo_single_password()
                elif choice == '3':
                    self.batch_performance_test()
                elif choice == '4':
                    if hasattr(self.cracker.stats, 'attack_history') and self.cracker.stats.attack_history:
                        self.cracker.stats.plot_performance()
                        report = self.cracker.stats.generate_performance_report()
                        print("\nPerformance Report:")
                        print(json.dumps(report, indent=2))
                    else:
                        print("No data available. Run some tests first.")
                elif choice == '5':
                    print("Exiting demo. Goodbye!")
                    break
                else:
                    print("Please enter a number between 1 and 5.")
                    
            except KeyboardInterrupt:
                print("\nExiting demo. Goodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    """Main function"""
    demo = EnhancedPasswordCrackerDemo()
    demo.run()

if __name__ == "__main__":
    main()
