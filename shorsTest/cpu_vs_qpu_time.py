#!/usr/bin/env python3
"""
plot_cpu_vs_qpu.py

Simple script to plot CPU vs QPU execution time comparison.
X-axis: N (number to factor)
Y-axis: Average execution time (seconds)
Blue line: QPU (quantum hardware)
Red line: CPU (simulation)

Usage:
  python3 plot_cpu_vs_qpu.py
  python3 plot_cpu_vs_qpu.py --results_dir results/
  python3 plot_cpu_vs_qpu.py --output my_plot.png
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
            # Extract mode from path (e.g., 'results/generic_sim_1/results.csv')
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


def plot_cpu_vs_qpu(df, output_file='cpu_vs_qpu_time.png'):
    """
    Plot CPU vs QPU: Time vs N
    - Blue line: QPU
    - Red line: CPU
    """
    
    # Filter successful runs only
    successful = df[df['success'] == True].copy()
    
    if len(successful) == 0:
        print("❌ No successful runs found!")
        return
    
    # Separate CPU and QPU data
    cpu_data = successful[successful['mode'] == 'sim']
    qpu_data = successful[successful['mode'] == 'quantum']
    
    if len(cpu_data) == 0 and len(qpu_data) == 0:
        print("❌ No CPU or QPU data found!")
        print("Available modes:", successful['mode'].unique())
        return
    
    # Create figure with larger size
    plt.figure(figsize=(12, 7))
    
    # Plot CPU data (RED)
    if len(cpu_data) > 0:
        cpu_avg = cpu_data.groupby('N')['total_time'].mean().sort_index()
        n_values_cpu = list(cpu_avg.index)
        times_cpu = list(cpu_avg.values)
        
        plt.plot(n_values_cpu, times_cpu, 
                 marker='o', 
                 linestyle='-', 
                 label='CPU (Simulation)', 
                 color='red', 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
        
        print(f"CPU Data Points:")
        for n, t in zip(n_values_cpu, times_cpu):
            num_runs = len(cpu_data[cpu_data['N'] == n])
            print(f"  N={n}: {t:.3f}s (averaged over {num_runs} runs)")
    
    # Plot QPU data (BLUE)
    if len(qpu_data) > 0:
        qpu_avg = qpu_data.groupby('N')['total_time'].mean().sort_index()
        n_values_qpu = list(qpu_avg.index)
        times_qpu = list(qpu_avg.values)
        
        plt.plot(n_values_qpu, times_qpu, 
                 marker='^', 
                 linestyle='-', 
                 label='QPU (Quantum Hardware)', 
                 color='blue', 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
        
        print(f"\nQPU Data Points:")
        for n, t in zip(n_values_qpu, times_qpu):
            num_runs = len(qpu_data[qpu_data['N'] == n])
            print(f"  N={n}: {t:.3f}s (averaged over {num_runs} runs)")
    
    # Get all unique N values for x-axis ticks
    all_n = sorted(successful['N'].unique())
    plt.xticks(all_n, [str(n) for n in all_n], fontsize=12)
    
    # Labels and styling
    plt.xlabel('N (Number to Factor)', fontsize=14, fontweight='bold')
    plt.ylabel('Average Execution Time (seconds)', fontsize=14, fontweight='bold')
    plt.title('CPU vs QPU Performance Comparison', fontsize=16, fontweight='bold')
    plt.legend(fontsize=13, loc='best', framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Graph saved: {output_file}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Plot CPU vs QPU performance comparison"
    )
    parser.add_argument('--results_dir', default='results', 
                        help='Results directory (default: results)')
    parser.add_argument('--output', default='cpu_vs_qpu_time.png', 
                        help='Output filename (default: cpu_vs_qpu_time.png)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("CPU vs QPU Performance Comparison - Time vs N")
    print("="*70 + "\n")
    
    # Discover result files
    files = auto_discover_results(args.results_dir)
    if not files:
        print(f"❌ No result files found in {args.results_dir}/")
        print(f"\nLooking for files matching: {args.results_dir}/*/results.csv")
        return
    
    print(f"Found {len(files)} result files\n")
    
    # Load data
    df = load_combined_data(files)
    if df is None or len(df) == 0:
        print("❌ No data loaded!")
        return
    
    # Generate plot
    plot_cpu_vs_qpu(df, args.output)


if __name__ == '__main__':
    main()