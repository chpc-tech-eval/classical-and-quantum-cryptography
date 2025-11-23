#!/usr/bin/env python3
"""
analyze.py

Analyze and visualize Shor's algorithm results from CSV data.

Usage:
  python3 analyze.py                    # Auto-scan results/ folder
  python3 analyze.py shor_results.csv   # Analyze single file
  python3 analyze.py --graphs all       # Generate all graphs from results/
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import glob


# Auto-discover all CSV files in results/ directory
def auto_discover_results(results_dir='results'):
    """Automatically find all results.csv files in results/ subdirectories."""
    pattern = f"{results_dir}/*/results.csv"
    files = glob.glob(pattern)
    
    if not files:
        # Try alternate pattern
        pattern = f"{results_dir}/*/*.csv"
        files = glob.glob(pattern)
    
    if files:
        print(f"Found {len(files)} result files:")
        for f in files:
            print(f"  • {f}")
        return files
    else:
        print(f"No CSV files found in {results_dir}/")
        return None


# Load results from CSV file
def load_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        print(f"File not found: {csv_file}")
        return None
    except Exception as e:
        print(f"Error loading {csv_file}: {e}")
        return None


# Load and combine multiple CSV files
def load_combined_data(files):
    """Load and combine multiple CSV files with mode detection."""
    dataframes = []
    
    for file in files:
        df = load_data(file)
        if df is not None:
            # Extract mode from path (e.g., 'results/actual_sim_1/results.csv')
            path_parts = Path(file).parent.name.split('_')
            
            if len(path_parts) >= 2:
                implementation = path_parts[0]  # 'generic' or 'actual'
                mode = path_parts[1]            # 'sim', 'gpu', 'quantum', 'parallel'
                
                df['implementation'] = implementation
                df['mode'] = mode
                df['source_file'] = str(file)
                
                dataframes.append(df)
                print(f"  ✓ Loaded {len(df)} rows from {file} ({implementation}/{mode})")
    
    if dataframes:
        combined = pd.concat(dataframes, ignore_index=True)
        print(f"\n✓ Combined {len(combined)} total results from {len(files)} files")
        return combined
    
    return None


# Print summary statistics
def print_summary(df):
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}\n")
    
    print(f"Total runs: {len(df)}")
    print(f"Successful: {df['success'].sum()} ({100*df['success'].mean():.1f}%)")
    print(f"Failed: {(~df['success']).sum()} ({100*(1-df['success'].mean()):.1f}%)")
    
    # Implementation breakdown
    if 'implementation' in df.columns:
        print(f"\nBy Implementation:")
        for impl in sorted(df['implementation'].unique()):
            impl_df = df[df['implementation'] == impl]
            print(f"  {impl.capitalize()}: {len(impl_df)} runs ({100*impl_df['success'].mean():.1f}% success)")
    
    # Hardware mode breakdown
    if 'mode' in df.columns:
        print(f"\nBy Hardware Mode:")
        for mode in sorted(df['mode'].unique()):
            mode_df = df[df['mode'] == mode]
            mode_name = {'sim': 'CPU', 'gpu': 'GPU', 'quantum': 'QPU', 'parallel': 'CPU/Parallel'}.get(mode, mode.upper())
            print(f"  {mode_name}: {len(mode_df)} runs ({100*mode_df['success'].mean():.1f}% success)")
    
    print(f"\nNumbers factored (N):")
    print(f"  Range: {df['N'].min()} to {df['N'].max()}")
    print(f"  Unique values: {df['N'].nunique()}")
    print(f"  Values tested: {sorted(df['N'].unique())}")
    
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
    
    filename = f'{output_dir}/success_rate_by_n.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot timing breakdown
def plot_timing_breakdown(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot timing")
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
    
    filename = f'{output_dir}/timing_breakdown.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot qubit requirements vs N
def plot_qubits_vs_n(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    qubits_by_n = df.groupby('N')['total_qubits'].mean()
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
    
    filename = f'{output_dir}/qubits_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
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
    
    filename = f'{output_dir}/depth_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot execution time vs N
def plot_execution_time_vs_n(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot execution time")
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
    
    filename = f'{output_dir}/execution_time_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot success rate vs number of shots
def plot_shots_vs_success(df, output_dir='plots'):
    Path(output_dir).mkdir(exist_ok=True)
    
    success_by_shots = df.groupby('shots')['success'].agg(['sum', 'count'])
    success_by_shots['rate'] = success_by_shots['sum'] / success_by_shots['count']
    
    if len(success_by_shots) < 2:
        print("⚠ Need multiple shot values to plot")
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(success_by_shots.index, success_by_shots['rate'] * 100, 
             'o-', markersize=10, linewidth=2)
    plt.xlabel('Number of Shots', fontsize=12)
    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.title('Success Rate vs Number of Measurements', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    filename = f'{output_dir}/shots_vs_success.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot time vs shots
def plot_time_vs_shots(df, output_dir='plots'):
    """Plot execution time vs number of shots."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot time vs shots")
        return
    
    if 'shots' not in successful.columns or successful['shots'].nunique() < 2:
        print("⚠ Need multiple shot values to plot time vs shots")
        return
    
    time_by_shots = successful.groupby('shots')['total_time'].agg(['mean', 'std'])
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(time_by_shots.index, time_by_shots['mean'], yerr=time_by_shots['std'],
                 fmt='o-', capsize=5, capthick=2, markersize=8, linewidth=2, color='#45B7D1')
    plt.xlabel('Number of Shots', fontsize=12)
    plt.ylabel('Total Time (seconds)', fontsize=12)
    plt.title('Execution Time vs Number of Shots', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    filename = f'{output_dir}/time_vs_shots.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot time vs base (a)
def plot_time_vs_a(df, output_dir='plots'):
    """Plot execution time vs base value 'a'."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot time vs a")
        return
    
    if 'a' not in successful.columns:
        print("⚠ Column 'a' not found (generic implementation doesn't vary 'a')")
        return
    
    if successful['a'].nunique() < 2:
        print("⚠ Need multiple 'a' values to plot")
        return
    
    time_by_a = successful.groupby('a')['total_time'].agg(['mean', 'std', 'count'])
    time_by_a = time_by_a[time_by_a['count'] >= 2]  # Only show 'a' values with multiple runs
    
    if len(time_by_a) < 2:
        print("⚠ Not enough data points for time vs a")
        return
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(time_by_a.index, time_by_a['mean'], yerr=time_by_a['std'],
                 fmt='o-', capsize=5, capthick=2, markersize=8, linewidth=2, color='#FF6B6B')
    plt.xlabel('Base (a)', fontsize=12)
    plt.ylabel('Total Time (seconds)', fontsize=12)
    plt.title('Execution Time vs Base Value', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    filename = f'{output_dir}/time_vs_a.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Plot time vs N (factored number size)
def plot_time_vs_n(df, output_dir='plots'):
    """Plot execution time vs N (problem size)."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot time vs N")
        return
    
    time_by_n = successful.groupby('N')['total_time'].agg(['mean', 'std'])
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(time_by_n.index, time_by_n['mean'], yerr=time_by_n['std'],
                 fmt='o-', capsize=5, capthick=2, markersize=8, linewidth=2, color='#4ECDC4')
    plt.xlabel('N (number to factor)', fontsize=12)
    plt.ylabel('Total Time (seconds)', fontsize=12)
    plt.title('Execution Time vs Problem Size', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    filename = f'{output_dir}/time_vs_n.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Hardware comparison (CPU vs GPU vs QPU) - FIXED VERSION
def plot_hardware_comparison(df, output_dir='plots'):
    """Plot N vs Time for different hardware modes with discrete N values."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot hardware comparison")
        return
    
    if 'mode' not in successful.columns:
        print("⚠ Column 'mode' not found - run with multiple hardware results")
        return
    
    modes = successful['mode'].unique()
    if len(modes) < 1:
        print("⚠ No hardware modes found")
        return
    
    plt.figure(figsize=(12, 7))
    
    # Color mapping: RED for CPU/parallel, GREEN for GPU, BLUE for QPU
    colors = {
        'sim': 'red',
        'cpu': 'red',
        'parallel': 'red',
        'gpu': 'green',
        'quantum': 'blue',
        'qpu': 'blue'
    }
    
    # Label mapping
    labels = {
        'sim': 'CPU',
        'cpu': 'CPU',
        'parallel': 'CPU/Parallel',
        'gpu': 'GPU',
        'quantum': 'QPU',
        'qpu': 'QPU'
    }
    
    # Marker styles
    markers = {
        'sim': 'o',
        'cpu': 'o',
        'parallel': 'o',
        'gpu': 's',
        'quantum': '^',
        'qpu': '^'
    }
    
    # Get all unique N values (discrete points only)
    all_n_values = sorted(successful['N'].unique())
    
    # Plot each mode
    for mode in sorted(modes):
        mode_data = successful[successful['mode'] == mode]
        
        # Group by N and get mean time for each discrete N
        time_by_n = mode_data.groupby('N')['total_time'].mean().sort_index()
        
        # Get discrete N values for this mode
        n_values = list(time_by_n.index)
        times = list(time_by_n.values)
        
        color = colors.get(mode, 'gray')
        label = labels.get(mode, mode.upper())
        marker = markers.get(mode, 'o')
        
        # Plot with discrete points connected by lines
        plt.plot(n_values, times, 
                 marker=marker, 
                 linestyle='-', 
                 label=label, 
                 color=color, 
                 markersize=10, 
                 linewidth=2.5, 
                 alpha=0.8)
    
    # Set x-axis to show ONLY the discrete N values tested
    plt.xticks(all_n_values, [str(n) for n in all_n_values], fontsize=11)
    
    plt.xlabel('N (number to factor)', fontsize=13)
    plt.ylabel('Execution Time (seconds)', fontsize=13)
    plt.title('Hardware Performance Comparison', fontsize=15, fontweight='bold')
    plt.legend(fontsize=12, loc='best', framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    filename = f'{output_dir}/hardware_comparison.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Generate a text report
def generate_report(df, output_file='shor_report.txt'):
    with open(output_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("SHOR'S ALGORITHM ANALYSIS REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Total Runs: {len(df)}\n")
        f.write(f"Success Rate: {100*df['success'].mean():.1f}%\n\n")
        
        # Implementation breakdown
        if 'implementation' in df.columns:
            f.write("By Implementation:\n")
            for impl in sorted(df['implementation'].unique()):
                impl_df = df[df['implementation'] == impl]
                success_rate = 100 * impl_df['success'].mean()
                f.write(f"  {impl.capitalize()}: {len(impl_df)} runs ({success_rate:.1f}% success)\n")
            f.write("\n")
        
        # Hardware breakdown
        if 'mode' in df.columns:
            f.write("By Hardware Mode:\n")
            for mode in sorted(df['mode'].unique()):
                mode_df = df[df['mode'] == mode]
                mode_name = {'sim': 'CPU', 'gpu': 'GPU', 'quantum': 'QPU', 'parallel': 'CPU/Parallel'}.get(mode, mode.upper())
                success_rate = 100 * mode_df['success'].mean()
                avg_time = mode_df[mode_df['success']]['total_time'].mean() if mode_df['success'].any() else 0
                f.write(f"  {mode_name}: {len(mode_df)} runs ({success_rate:.1f}% success, avg {avg_time:.2f}s)\n")
            f.write("\n")
        
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
    
    print(f"✓ Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Shor's algorithm results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 analyze.py                          # Auto-scan results/ folder
  python3 analyze.py --graphs all             # Generate all graphs
  python3 analyze.py --graphs hardware        # Only hardware comparison
  python3 analyze.py results/actual_sim_1/results.csv  # Analyze single file
        """
    )
    parser.add_argument('csv_file', nargs='?', help='CSV file with results (optional, auto-discovers if not provided)')
    parser.add_argument('--graphs', choices=['all', 'timing', 'scaling', 'success', 'hardware'], 
                        default='all', help='Which graphs to generate')
    parser.add_argument('--output_dir', default='plots', help='Output directory for plots')
    parser.add_argument('--report', default='shor_report.txt', help='Output report file')
    parser.add_argument('--results_dir', default='results', help='Directory to scan for result files')
    
    args = parser.parse_args()
    
    # Load data
    if args.csv_file:
        # Single file specified
        print(f"Loading single file: {args.csv_file}")
        df = load_data(args.csv_file)
    else:
        # Auto-discover all results
        print(f"Auto-discovering results in {args.results_dir}/")
        files = auto_discover_results(args.results_dir)
        if not files:
            print("\n❌ No result files found!")
            print(f"Make sure you have CSV files in {args.results_dir}/*/")
            return
        df = load_combined_data(files)
    
    if df is None or len(df) == 0:
        print("❌ No data loaded!")
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
        plot_time_vs_shots(df, args.output_dir)
        plot_time_vs_a(df, args.output_dir)
        plot_time_vs_n(df, args.output_dir)
    
    if args.graphs in ['all', 'scaling']:
        plot_qubits_vs_n(df, args.output_dir)
        plot_depth_vs_n(df, args.output_dir)
    
    if args.graphs in ['all', 'hardware']:
        plot_hardware_comparison(df, args.output_dir)
    
    # Generate report
    generate_report(df, args.report)
    
    print(f"\n{'='*70}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'='*70}\n")
    print(f"Plots saved to: {args.output_dir}/")
    print(f"Report saved to: {args.report}")


if __name__ == '__main__':
    main()