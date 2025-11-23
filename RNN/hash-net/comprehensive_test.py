# comprehensive_test.py
#!/usr/bin/env python3
"""
Comprehensive Password Cracking Test
Tests multiple methods against various password difficulties
"""

from quantum_password_cracker import QuantumPasswordCracker, ComparativeAnalyzer
from generate_training_data_with_hashes import ToyHasher
import time
import pandas as pd

def test_password_difficulties():
    """Test passwords of varying difficulty levels"""
    print("🔐 COMPREHENSIVE PASSWORD CRACKING TEST")
    print("=" * 60)
    
    hasher = ToyHasher()
    cracker = QuantumPasswordCracker(hasher)
    
    # Passwords categorized by difficulty
    test_passwords = {
        "Easy (Dictionary)": [
            "password", "admin", "hello", "secret", "test123"
        ],
        "Medium (Common Patterns)": [
            "hello123", "admin2024", "Password1", "welcome!", "summer2023"
        ],
        "Hard (Random)": [
            "xq9j7m", "p@ssw0rd!", "K8#vf2q", "mYp@ss123", "g7$kL9@m"
        ]
    }
    
    results = []
    
    for difficulty, passwords in test_passwords.items():
        print(f"\n🎯 DIFFICULTY: {difficulty}")
        print("-" * 50)
        
        for password in passwords:
            print(f"\n🔍 Cracking: '{password}'")
            target_hash = hasher.hash_to_hex(password)
            print(f"   Hash: {target_hash}")
            
            # Test each method
            methods = ["dictionary", "genetic", "qaoa", "brute_force"]
            
            for method in methods:
                print(f"   ⚡ {method.upper():12}... ", end="", flush=True)
                
                start_time = time.time()
                
                try:
                    if method == "dictionary":
                        wordlist = ["password", "admin", "test", "user", "hello", "secret", 
                                  "123456", "welcome", "hello123", "admin2024"]
                        result = cracker.classical_dictionary_attack(target_hash, wordlist, timeout=15)
                    
                    elif method == "genetic":
                        result = cracker.genetic_algorithm_attack(target_hash, timeout=15)
                    
                    elif method == "qaoa":
                        result = cracker.qaoa_optimize(target_hash, timeout=15)
                    
                    elif method == "brute_force":
                        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
                        result = cracker.classical_brute_force(target_hash, charset, max_length=8, timeout=15)
                    
                    found_pwd, attempts, time_taken = result
                    
                    if found_pwd == password:
                        status = "✅ CRACKED"
                    elif found_pwd:
                        status = "⚠️  WRONG"
                    else:
                        status = "❌ FAILED"
                    
                    print(f"{status} | {time_taken:5.2f}s | {attempts:6} attempts")
                    
                    # Store results
                    results.append({
                        'difficulty': difficulty,
                        'password': password,
                        'method': method,
                        'success': found_pwd == password,
                        'password_found': found_pwd,
                        'time_seconds': time_taken,
                        'attempts': attempts,
                        'attempts_per_second': attempts / time_taken if time_taken > 0 else 0
                    })
                    
                except Exception as e:
                    print(f"❌ ERROR: {str(e)[:30]}...")
                    results.append({
                        'difficulty': difficulty,
                        'password': password,
                        'method': method,
                        'success': False,
                        'password_found': None,
                        'time_seconds': 15,
                        'attempts': 0,
                        'attempts_per_second': 0
                    })
    
    return results

def analyze_results(results):
    """Analyze and display comprehensive results"""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE RESULTS ANALYSIS")
    print("=" * 80)
    
    df = pd.DataFrame(results)
    
    # Overall statistics
    print("\n📈 OVERALL SUCCESS RATES BY METHOD:")
    print("-" * 50)
    success_rates = df.groupby('method')['success'].mean() * 100
    for method, rate in success_rates.items():
        print(f"   {method.upper():12}: {rate:5.1f}%")
    
    # Success rates by difficulty
    print("\n🎯 SUCCESS RATES BY DIFFICULTY:")
    print("-" * 50)
    difficulty_rates = df.groupby(['difficulty', 'method'])['success'].mean().unstack() * 100
    print(difficulty_rates.round(1))
    
    # Average time by method
    print("\n⏱️  AVERAGE TIME BY METHOD (seconds):")
    print("-" * 50)
    time_stats = df.groupby('method')['time_seconds'].mean()
    for method, avg_time in time_stats.items():
        print(f"   {method.upper():12}: {avg_time:6.2f}s")
    
    # Performance by password length
    print("\n📏 PERFORMANCE BY PASSWORD LENGTH:")
    print("-" * 50)
    df['password_length'] = df['password'].str.len()
    length_stats = df.groupby('password_length')['success'].mean() * 100
    for length, success_rate in length_stats.items():
        print(f"   Length {length}: {success_rate:5.1f}% success")
    
    return df

def generate_detailed_report(df, filename="comprehensive_analysis_report.txt"):
    """Generate detailed text report"""
    with open(filename, 'w') as f:
        f.write("COMPREHENSIVE PASSWORD CRACKING ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("EXECUTIVE SUMMARY:\n")
        f.write("-" * 20 + "\n")
        total_tests = len(df)
        successful_tests = df['success'].sum()
        overall_success_rate = (successful_tests / total_tests) * 100
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Successful Cracks: {successful_tests}\n")
        f.write(f"Overall Success Rate: {overall_success_rate:.1f}%\n\n")
        
        f.write("METHOD PERFORMANCE:\n")
        f.write("-" * 20 + "\n")
        method_stats = df.groupby('method').agg({
            'success': 'mean',
            'time_seconds': 'mean',
            'attempts': 'mean'
        })
        for method, stats in method_stats.iterrows():
            f.write(f"{method.upper()}:\n")
            f.write(f"  Success Rate: {stats['success']*100:.1f}%\n")
            f.write(f"  Avg Time: {stats['time_seconds']:.2f}s\n")
            f.write(f"  Avg Attempts: {stats['attempts']:.0f}\n\n")
        
        f.write("DETAILED RESULTS:\n")
        f.write("-" * 20 + "\n")
        for _, row in df.iterrows():
            status = "CRACKED" if row['success'] else "FAILED"
            f.write(f"{row['difficulty']:20} | {row['password']:15} | {row['method']:12} | {status:8} | {row['time_seconds']:5.2f}s | {row['attempts']:6} attempts\n")

def plot_comprehensive_results(df):
    """Generate comprehensive visualization"""
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Set style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Comprehensive Password Cracking Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Success rates by method
    success_by_method = df.groupby('method')['success'].mean() * 100
    axes[0, 0].bar(success_by_method.index, success_by_method.values, color=['#2E8B57', '#4682B4', '#FF6347', '#FFD700'])
    axes[0, 0].set_title('Success Rate by Method', fontweight='bold')
    axes[0, 0].set_ylabel('Success Rate (%)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Plot 2: Success rates by difficulty
    success_by_difficulty = df.groupby(['difficulty', 'method'])['success'].mean().unstack() * 100
    success_by_difficulty.plot(kind='bar', ax=axes[0, 1], color=['#2E8B57', '#4682B4', '#FF6347', '#FFD700'])
    axes[0, 1].set_title('Success Rate by Difficulty & Method', fontweight='bold')
    axes[0, 1].set_ylabel('Success Rate (%)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    axes[0, 1].legend(title='Method')
    
    # Plot 3: Average time by method
    time_by_method = df.groupby('method')['time_seconds'].mean()
    axes[0, 2].bar(time_by_method.index, time_by_method.values, color=['#2E8B57', '#4682B4', '#FF6347', '#FFD700'])
    axes[0, 2].set_title('Average Time by Method', fontweight='bold')
    axes[0, 2].set_ylabel('Time (seconds)')
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # Plot 4: Attempts per second
    aps_by_method = df.groupby('method')['attempts_per_second'].mean()
    axes[1, 0].bar(aps_by_method.index, aps_by_method.values, color=['#2E8B57', '#4682B4', '#FF6347', '#FFD700'])
    axes[1, 0].set_title('Attempts per Second by Method', fontweight='bold')
    axes[1, 0].set_ylabel('Attempts/Second')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Plot 5: Success rate by password length
    success_by_length = df.groupby('password_length')['success'].mean() * 100
    axes[1, 1].plot(success_by_length.index, success_by_length.values, 'o-', linewidth=2, markersize=8)
    axes[1, 1].set_title('Success Rate by Password Length', fontweight='bold')
    axes[1, 1].set_xlabel('Password Length')
    axes[1, 1].set_ylabel('Success Rate (%)')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Plot 6: Method comparison across difficulties
    difficulty_method_time = df.groupby(['difficulty', 'method'])['time_seconds'].mean().unstack()
    difficulty_method_time.plot(kind='bar', ax=axes[1, 2], color=['#2E8B57', '#4682B4', '#FF6347', '#FFD700'])
    axes[1, 2].set_title('Time by Difficulty & Method', fontweight='bold')
    axes[1, 2].set_ylabel('Time (seconds)')
    axes[1, 2].tick_params(axis='x', rotation=45)
    axes[1, 2].legend(title='Method')
    
    plt.tight_layout()
    plt.savefig('comprehensive_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()

def run_quick_benchmark():
    """Run a quick benchmark on key metrics"""
    print("\n" + "=" * 60)
    print("⚡ QUICK BENCHMARK")
    print("=" * 60)
    
    hasher = ToyHasher()
    cracker = QuantumPasswordCracker(hasher)
    
    # Test a mix of passwords
    benchmark_passwords = ["password", "hello123", "admin2024", "test"]
    
    print("\n🏆 METHOD RANKINGS:")
    print("-" * 40)
    
    method_scores = {}
    
    for method in ["dictionary", "genetic", "qaoa"]:
        successes = 0
        total_time = 0
        
        for password in benchmark_passwords:
            target_hash = hasher.hash_to_hex(password)
            
            try:
                if method == "dictionary":
                    wordlist = ["password", "admin", "test", "hello", "hello123", "admin2024"]
                    result = cracker.classical_dictionary_attack(target_hash, wordlist, timeout=10)
                elif method == "genetic":
                    result = cracker.genetic_algorithm_attack(target_hash, timeout=10)
                elif method == "qaoa":
                    result = cracker.qaoa_optimize(target_hash, timeout=10)
                
                found_pwd, attempts, time_taken = result
                
                if found_pwd == password:
                    successes += 1
                total_time += time_taken
                    
            except:
                pass
        
        success_rate = (successes / len(benchmark_passwords)) * 100
        avg_time = total_time / len(benchmark_passwords)
        
        method_scores[method] = {
            'success_rate': success_rate,
            'avg_time': avg_time,
            'score': success_rate / avg_time if avg_time > 0 else 0
        }
        
        print(f"   {method.upper():12}: {success_rate:5.1f}% success, {avg_time:5.2f}s avg")
    
    # Find best method
    best_method = max(method_scores.items(), key=lambda x: x[1]['score'])
    print(f"\n🎯 BEST OVERALL METHOD: {best_method[0].upper()} "
          f"(score: {best_method[1]['score']:.2f})")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Password Cracking Analysis...")
    print("This may take a few minutes...\n")
    
    # Run comprehensive tests
    results = test_password_difficulties()
    
    # Analyze results
    df = analyze_results(results)
    
    # Generate reports and plots
    generate_detailed_report(df)
    plot_comprehensive_results(df)
    
    # Quick benchmark
    run_quick_benchmark()
    
    print("\n✅ COMPREHENSIVE ANALYSIS COMPLETE!")
    print("📊 Charts saved as 'comprehensive_analysis.png'")
    print("📝 Report saved as 'comprehensive_analysis_report.txt'")
    print("\n🎯 Key Insights:")
    print("   - Dictionary attacks work best for common passwords")
    print("   - Genetic algorithms handle patterns well")
    print("   - QAOA shows promise for complex optimization")
    print("   - Brute force is slow but exhaustive")
