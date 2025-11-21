#!/usr/bin/env python3
"""
analyze.py

Analyze and visualize Shor's algorithm results from CSV data.

Usage:
  python3 analyze.py shor_results.csv
  python3 analyze.py shor_results.csv --graphs all
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# Load results from CSV file
def load_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} results from {csv_file}")
        return df
    except FileNotFoundError:
        print(f"File not found: {csv_file}")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


# Print summary statistics
def print_summary(df):
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}\n")
    
    print(f"Total runs: {len(df)}")
    print(f"Successful: {df['success'].sum()} ({100*df['success'].mean():.1f}%)")
    print(f"Failed: {(~df['success']).sum()} ({100*(1-df['success'].mean()):.1f}%)")
    
    print(f"\nNumbers factored (N):")
    print(f"  Range: {df['N'].min()} to {df['N'].max()}")
    print(f"  Unique values: {df['N'].nunique()}")
    
    if df['success'].any():
        successful = df[df['success']]
        print(f"\nSuccessful runs:")
        print(f"  Average total time: {successful['total_time'].mean():.2f}s")
        print(f"  Average circuit depth: {successful['circuit_depth'].mean():.0f}")
        print(f"  Average qubits used: {successful['total_qubits'].mean():.1f}")
        
        print(f"\nPeriod finding accuracy:")
        if 'matches_classical' in successful.columns:
            matches = successful['matches_classical'].apply(lambda x: x == True or x == 'True').sum()
            print(f"  Quantum period matched classical: {matches}/{len(successful)} ({100*matches/len(successful):.1f}%)")

# Plot success rate vs N
def plot_success_rate_by_n(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    success_by_n = df.groupby('N')['success'].agg(['sum', 'count'])
    success_by_n['rate'] = success_by_n['sum'] / success_by_n['count']
    
    plt.figure(figsize=(10, 6))
    plt.bar(success_by_n.index, success_by_n['rate'] * 100, alpha=0.7, edgecolor='black')
    plt.xlabel('N (number to factor)', fontsize=12)
    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.title('Shor\'s Algorithm Success Rate by N', fontsize=14)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Save the plot as png
    filename = f'{output_dir}/success_rate_by_n.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    plt.close()


# Plot timing breakdown
def plot_timing_breakdown(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("No successful runs to plot timing")
        return
    
    time_cols = ['preprocessing_time', 'circuit_time', 'transpile_time', 
                 'execution_time', 'postprocess_time']
    
    avg_times = successful[time_cols].mean()
    
    plt.figure(figsize=(10, 6))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    plt.bar(range(len(avg_times)), avg_times, color=colors, alpha=0.7, edgecolor='black')
    plt.xticks(range(len(avg_times)), 
               ['Preprocessing', 'Circuit\nConstruction', 'Transpilation', 
                'Execution', 'Post-processing'],
               rotation=45, ha='right')
    plt.ylabel('Average Time (seconds)', fontsize=12)
    plt.title('Timing Breakdown of Shor\'s Algorithm', fontsize=14)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Save the plot as png
    filename = f'{output_dir}/timing_breakdown.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    plt.close()


# Plot qubit requirements vs N
def plot_qubits_vs_n(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    # Group by N and get average qubits
    qubits_by_n = df.groupby('N')['total_qubits'].mean()
    
    # Theoretical: 3 * ceil(log2(N))
    n_values = np.array(qubits_by_n.index)
    theoretical = 3 * np.ceil(np.log2(n_values))
    
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, qubits_by_n.values, 'o-', label='Actual', markersize=8, linewidth=2)
    plt.plot(n_values, theoretical, 's--', label='Theoretical (3⌈log₂N⌉)', 
             markersize=6, linewidth=2, alpha=0.7)
    plt.xlabel('N (number to factor)', fontsize=12)
    plt.ylabel('Number of Qubits', fontsize=12)
    plt.title('Qubit Requirements vs Problem Size', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Save the plot as png
    filename = f'{output_dir}/qubits_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    plt.close()


# Plot circuit depth vs N
def plot_depth_vs_n(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    depth_by_n = df.groupby('N')[['circuit_depth', 'transpiled_depth']].mean()
    
    plt.figure(figsize=(10, 6))
    x = np.array(depth_by_n.index)
    width = (x[1] - x[0]) * 0.35 if len(x) > 1 else 2
    
    plt.bar(x - width/2, depth_by_n['circuit_depth'], width, 
            label='Original Circuit', alpha=0.7, edgecolor='black')
    plt.bar(x + width/2, depth_by_n['transpiled_depth'], width, 
            label='Transpiled Circuit', alpha=0.7, edgecolor='black')
    
    plt.xlabel('N (number to factor)', fontsize=12)
    plt.ylabel('Circuit Depth', fontsize=12)
    plt.title('Circuit Depth vs Problem Size', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Save the plot as png
    filename = f'{output_dir}/depth_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    plt.close()


# Plot execution time vs N
def plot_execution_time_vs_n(df, output_dir='plots'):
    """Plot execution time vs N."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("No successful runs to plot execution time")
        return
    
    time_by_n = successful.groupby('N')['total_time'].agg(['mean', 'std'])
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(time_by_n.index, time_by_n['mean'], yerr=time_by_n['std'],
                 fmt='o-', capsize=5, capthick=2, markersize=8, linewidth=2)
    plt.xlabel('N (number to factor)', fontsize=12)
    plt.ylabel('Total Time (seconds)', fontsize=12)
    plt.title('Execution Time vs Problem Size', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Save the plot as png
    filename = f'{output_dir}/execution_time_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    plt.close()


# Plot success rate vs number of shots
def plot_shots_vs_success(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    success_by_shots = df.groupby('shots')['success'].agg(['sum', 'count'])
    success_by_shots['rate'] = success_by_shots['sum'] / success_by_shots['count']
    
    if len(success_by_shots) < 2:
        print("Need multiple shot values to plot")
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(success_by_shots.index, success_by_shots['rate'] * 100, 
             'o-', markersize=10, linewidth=2)
    plt.xlabel('Number of Shots', fontsize=12)
    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.title('Success Rate vs Number of Measurements', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Save the plot as png
    filename = f'{output_dir}/shots_vs_success.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    plt.close()


# Generate a text report
def generate_report(df, output_file='shor_report.txt'):
    with open(output_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("SHOR'S ALGORITHM ANALYSIS REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Total Runs: {len(df)}\n")
        f.write(f"Success Rate: {100*df['success'].mean():.1f}%\n\n")
        
        f.write("Numbers Factored:\n")
        for n in sorted(df['N'].unique()):
            n_df = df[df['N'] == n]
            success_rate = 100 * n_df['success'].mean()
            f.write(f"  N={n}: {n_df['success'].sum()}/{len(n_df)} successful ({success_rate:.1f}%)\n")
        
        f.write("\n")
        
        if df['success'].any():
            successful = df[df['success']]
            f.write("Performance Metrics (Successful Runs):\n")
            f.write(f"  Average qubits: {successful['total_qubits'].mean():.1f}\n")
            f.write(f"  Average circuit depth: {successful['circuit_depth'].mean():.0f}\n")
            f.write(f"  Average execution time: {successful['total_time'].mean():.2f}s\n")
            f.write(f"  Fastest run: {successful['total_time'].min():.2f}s\n")
            f.write(f"  Slowest run: {successful['total_time'].max():.2f}s\n")
    
    print(f"Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze Shor's algorithm results")
    parser.add_argument('csv_file', help='CSV file with results')
    parser.add_argument('--graphs', choices=['all', 'timing', 'scaling', 'success'], 
                        default='all', help='Which graphs to generate')
    parser.add_argument('--output_dir', default='plots', help='Output directory for plots')
    parser.add_argument('--report', default='shor_report.txt', help='Output report file')
    
    args = parser.parse_args()
    
    # Load data
    df = load_data(args.csv_file)
    if df is None:
        return
    
    # Print summary
    print_summary(df)
    
    # Generate graphs
    print(f"\n{'='*70}")
    print("GENERATING VISUALIZATIONS")
    print(f"{'='*70}\n")
    
    if args.graphs in ['all', 'success']:
        plot_success_rate_by_n(df, args.output_dir)
        if 'shots' in df.columns and df['shots'].nunique() > 1:
            plot_shots_vs_success(df, args.output_dir)
    
    if args.graphs in ['all', 'timing']:
        plot_timing_breakdown(df, args.output_dir)
        plot_execution_time_vs_n(df, args.output_dir)
    
    if args.graphs in ['all', 'scaling']:
        plot_qubits_vs_n(df, args.output_dir)
        plot_depth_vs_n(df, args.output_dir)
    
    # Generate report
    generate_report(df, args.report)
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}\n")
    print(f"Plots saved to: {args.output_dir}/")
    print(f"Report saved to: {args.report}")


if __name__ == '__main__':
    main()
