#!/usr/bin/env python3
"""
plot_success_vs_shots.py

Plot success rate vs number of shots.
- X-axis: Shots (number of measurements)
- Y-axis: Success rate (%)
- Blue line: QPU (quantum hardware)
- Red line: CPU (simulation)

Usage:
  python3 plot_success_vs_shots.py
  python3 plot_success_vs_shots.py --results_dir results/
  python3 plot_success_vs_shots.py --output success_vs_shots.png
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


def plot_success_vs_shots(df, output_file='success_vs_shots.png'):
    """
    Plot success rate vs shots
    - Blue line: QPU
    - Red line: CPU
    """
    
    if 'shots' not in df.columns:
        print("❌ 'shots' column not found in data!")
        return
    
    # Check if we have multiple shot values
    shot_values = df['shots'].unique()
    if len(shot_values) < 2:
        print(f"⚠ Only {len(shot_values)} shot value(s) found. Need multiple values to plot.")
        print(f"Available shot value(s): {shot_values}")
        return
    
    # Separate CPU and QPU data
    cpu_data = df[df['mode'] == 'sim']
    qpu_data = df[df['mode'] == 'quantum']
    
    if len(cpu_data) == 0 and len(qpu_data) == 0:
        print("❌ No CPU or QPU data found!")
        print("Available modes:", df['mode'].unique())
        return
    
    # Create figure
    plt.figure(figsize=(12, 7))
    
    # Plot CPU data (RED)
    if len(cpu_data) > 0 and cpu_data['shots'].nunique() > 1:
        cpu_grouped = cpu_data.groupby('shots')['success'].agg(['sum', 'count'])
        cpu_grouped['rate'] = (cpu_grouped['sum'] / cpu_grouped['count']) * 100
        
        shots_cpu = list(cpu_grouped.index)
        rates_cpu = list(cpu_grouped['rate'].values)
        
        plt.plot(shots_cpu, rates_cpu, 
                 marker='o', 
                 linestyle='-', 
                 label='CPU (Simulation)', 
                 color='red', 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
        
        print(f"CPU Success Rates:")
        for shots, rate, count in zip(shots_cpu, rates_cpu, cpu_grouped['count']):
            print(f"  {shots} shots: {rate:.1f}% ({count} runs)")
    
    # Plot QPU data (BLUE)
    if len(qpu_data) > 0 and qpu_data['shots'].nunique() > 1:
        qpu_grouped = qpu_data.groupby('shots')['success'].agg(['sum', 'count'])
        qpu_grouped['rate'] = (qpu_grouped['sum'] / qpu_grouped['count']) * 100
        
        shots_qpu = list(qpu_grouped.index)
        rates_qpu = list(qpu_grouped['rate'].values)
        
        plt.plot(shots_qpu, rates_qpu, 
                 marker='^', 
                 linestyle='-', 
                 label='QPU (Quantum Hardware)', 
                 color='blue', 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
        
        print(f"\nQPU Success Rates:")
        for shots, rate, count in zip(shots_qpu, rates_qpu, qpu_grouped['count']):
            print(f"  {shots} shots: {rate:.1f}% ({count} runs)")
    
    # Labels and styling
    plt.xlabel('Number of Shots (Measurements)', fontsize=14, fontweight='bold')
    plt.ylabel('Success Rate (%)', fontsize=14, fontweight='bold')
    plt.title('Success Rate vs Number of Shots', fontsize=16, fontweight='bold')
    plt.legend(fontsize=13, loc='best', framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.ylim(0, 105)  # Success rate from 0-100%
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Graph saved: {output_file}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Plot success rate vs shots comparison"
    )
    parser.add_argument('--results_dir', default='results', 
                        help='Results directory (default: results)')
    parser.add_argument('--output', default='success_vs_shots.png', 
                        help='Output filename (default: success_vs_shots.png)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Success Rate vs Shots Comparison")
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
    plot_success_vs_shots(df, args.output)


if __name__ == '__main__':
    main()