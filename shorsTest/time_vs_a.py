#!/usr/bin/env python3
"""
plot_time_vs_a.py

Plot execution time vs base value 'a'.
- X-axis: a (base value for modular exponentiation)
- Y-axis: Average execution time (seconds)
- Blue line: QPU (quantum hardware)
- Red line: CPU (simulation)

Usage:
  python3 plot_time_vs_a.py
  python3 plot_time_vs_a.py --results_dir results/
  python3 plot_time_vs_a.py --output time_vs_a.png
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import glob
from pathlib import Path


def auto_discover_results(results_dir='results'):
    """Find all results.csv files in subdirectories."""
    pattern = f"{results_dir}/*/results.csv"
    files = glob.glob(pattern)
    
    if not files:
        pattern = f"{results_dir}/*/*.csv"
        files = glob.glob(pattern)
    
    return files if files else None


def load_combined_data(files):
    """Load and combine CSV files, extracting mode from path."""
    dataframes = []
    
    for file in files:
        try:
            df = pd.read_csv(file)
            # Extract mode from path
            path_parts = Path(file).parent.name.split('_')
            
            if len(path_parts) >= 2:
                mode = path_parts[1]  # 'sim', 'gpu', 'quantum'
                df['mode'] = mode
                dataframes.append(df)
                print(f"✓ Loaded {len(df)} rows from {file} (mode: {mode})")
        except Exception as e:
            print(f"⚠ Error loading {file}: {e}")
    
    if dataframes:
        combined = pd.concat(dataframes, ignore_index=True)
        print(f"\n✓ Combined {len(combined)} total results\n")
        return combined
    
    return None


def plot_time_vs_a(df, output_file='time_vs_a.png'):
    """
    Plot execution time vs base 'a'
    - Blue line: QPU
    - Red line: CPU
    """
    
    if 'a' not in df.columns:
        print("❌ 'a' column not found in data!")
        print("Note: Generic implementation may not have fixed 'a' values")
        return
    
    # Filter successful runs only
    successful = df[df['success'] == True].copy()
    
    if len(successful) == 0:
        print("❌ No successful runs found!")
        return
    
    # Check if we have multiple 'a' values
    a_values = successful['a'].unique()
    if len(a_values) < 2:
        print(f"⚠ Only {len(a_values)} 'a' value(s) found. Need multiple values to plot.")
        print(f"Available 'a' value(s): {a_values}")
        return
    
    # Separate CPU and QPU data
    cpu_data = successful[successful['mode'] == 'sim']
    qpu_data = successful[successful['mode'] == 'quantum']
    
    if len(cpu_data) == 0 and len(qpu_data) == 0:
        print("❌ No CPU or QPU data found!")
        print("Available modes:", successful['mode'].unique())
        return
    
    # Create figure
    plt.figure(figsize=(12, 7))
    
    # Plot CPU data (RED)
    if len(cpu_data) > 0 and cpu_data['a'].nunique() > 1:
        cpu_avg = cpu_data.groupby('a')['total_time'].mean().sort_index()
        
        a_cpu = list(cpu_avg.index)
        times_cpu = list(cpu_avg.values)
        
        plt.plot(a_cpu, times_cpu, 
                 marker='o', 
                 linestyle='-', 
                 label='CPU (Simulation)', 
                 color='red', 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
        
        print(f"CPU Execution Times by Base 'a':")
        for a, time in zip(a_cpu, times_cpu):
            num_runs = len(cpu_data[cpu_data['a'] == a])
            print(f"  a={a}: {time:.3f}s (averaged over {num_runs} runs)")
    
    # Plot QPU data (BLUE)
    if len(qpu_data) > 0 and qpu_data['a'].nunique() > 1:
        qpu_avg = qpu_data.groupby('a')['total_time'].mean().sort_index()
        
        a_qpu = list(qpu_avg.index)
        times_qpu = list(qpu_avg.values)
        
        plt.plot(a_qpu, times_qpu, 
                 marker='^', 
                 linestyle='-', 
                 label='QPU (Quantum Hardware)', 
                 color='blue', 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
        
        print(f"\nQPU Execution Times by Base 'a':")
        for a, time in zip(a_qpu, times_qpu):
            num_runs = len(qpu_data[qpu_data['a'] == a])
            print(f"  a={a}: {time:.3f}s (averaged over {num_runs} runs)")
    
    # Get all unique 'a' values for x-axis
    all_a = sorted(successful['a'].unique())
    plt.xticks(all_a, [str(int(a)) for a in all_a], fontsize=11)
    
    # Labels and styling
    plt.xlabel('Base Value (a)', fontsize=14, fontweight='bold')
    plt.ylabel('Average Execution Time (seconds)', fontsize=14, fontweight='bold')
    plt.title('Execution Time vs Base Value', fontsize=16, fontweight='bold')
    plt.legend(fontsize=13, loc='best', framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Graph saved: {output_file}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Plot execution time vs base 'a' comparison"
    )
    parser.add_argument('--results_dir', default='results', 
                        help='Results directory (default: results)')
    parser.add_argument('--output', default='time_vs_a.png', 
                        help='Output filename (default: time_vs_a.png)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Execution Time vs Base 'a' Comparison")
    print("="*70 + "\n")
    
    # Discover result files
    files = auto_discover_results(args.results_dir)
    if not files:
        print(f"❌ No result files found in {args.results_dir}/")
        return
    
    print(f"Found {len(files)} result files\n")
    
    # Load data
    df = load_combined_data(files)
    if df is None or len(df) == 0:
        print("❌ No data loaded!")
        return
    
    # Generate plot
    plot_time_vs_a(df, args.output)


if __name__ == '__main__':
    main()