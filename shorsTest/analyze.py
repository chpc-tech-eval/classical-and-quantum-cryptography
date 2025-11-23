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


# Hardware comparison (CPU vs GPU vs QPU)
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


# Implementation comparison (Generic vs Actual) for each hardware mode
def plot_implementation_comparison(df, output_dir='plots'):
    """Plot Generic vs Actual for each hardware mode separately."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot implementation comparison")
        return
    
    if 'implementation' not in successful.columns or 'mode' not in successful.columns:
        print("⚠ Need both 'implementation' and 'mode' columns")
        return
    
    modes = successful['mode'].unique()
    if len(modes) == 0:
        print("⚠ No hardware modes found")
        return
    
    # Color scheme for implementations
    impl_colors = {
        'generic': '#FF6B6B',  # Red-ish
        'actual': '#4ECDC4'    # Teal
    }
    
    impl_markers = {
        'generic': 'o',
        'actual': 's'
    }
    
    # Hardware mode names
    mode_names = {
        'sim': 'CPU',
        'cpu': 'CPU',
        'parallel': 'Parallel',
        'gpu': 'GPU',
        'quantum': 'QPU',
        'qpu': 'QPU'
    }
    
    # Create subplot for each hardware mode
    available_modes = sorted(modes)
    n_modes = len(available_modes)
    
    if n_modes == 0:
        print("⚠ No modes to plot")
        return
    
    # Determine subplot layout
    if n_modes == 1:
        fig, axes = plt.subplots(1, 1, figsize=(10, 6))
        axes = [axes]
    elif n_modes == 2:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    elif n_modes <= 4:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
    else:
        n_cols = 3
        n_rows = (n_modes + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
        axes = axes.flatten()
    
    # Plot each mode
    for idx, mode in enumerate(available_modes):
        ax = axes[idx]
        mode_data = successful[successful['mode'] == mode]
        
        # Get unique N values for this mode
        all_n_values = sorted(mode_data['N'].unique())
        
        # Plot generic and actual
        for impl in ['generic', 'actual']:
            impl_data = mode_data[mode_data['implementation'] == impl]
            
            if len(impl_data) == 0:
                continue
            
            time_by_n = impl_data.groupby('N')['total_time'].mean().sort_index()
            
            n_values = list(time_by_n.index)
            times = list(time_by_n.values)
            
            color = impl_colors.get(impl, 'gray')
            marker = impl_markers.get(impl, 'o')
            
            ax.plot(n_values, times,
                   marker=marker,
                   linestyle='-',
                   label=impl.capitalize(),
                   color=color,
                   markersize=10,
                   linewidth=2.5,
                   alpha=0.8)
        
        # Configure subplot
        ax.set_xticks(all_n_values)
        ax.set_xticklabels([str(n) for n in all_n_values], fontsize=10)
        ax.set_xlabel('N (number to factor)', fontsize=11)
        ax.set_ylabel('Execution Time (seconds)', fontsize=11)
        
        mode_name = mode_names.get(mode, mode.upper())
        ax.set_title(f'{mode_name}', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
    
    # Hide unused subplots
    for idx in range(n_modes, len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle('Generic vs Actual Implementation Comparison', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    filename = f'{output_dir}/implementation_comparison.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Alternative: Single combined plot with all modes
def plot_implementation_comparison_combined(df, output_dir='plots'):
    """Plot Generic vs Actual with subplots for each mode, side by side."""
    Path(output_dir).mkdir(exist_ok=True)
    
    successful = df[df['success']]
    if len(successful) == 0:
        print("⚠ No successful runs to plot implementation comparison")
        return
    
    if 'implementation' not in successful.columns or 'mode' not in successful.columns:
        print("⚠ Need both 'implementation' and 'mode' columns")
        return
    
    modes = sorted(successful['mode'].unique())
    
    # Hardware mode display order and names
    mode_order = ['sim', 'parallel', 'gpu', 'quantum']
    mode_names = {
        'sim': 'CPU',
        'cpu': 'CPU',
        'parallel': 'Parallel',
        'gpu': 'GPU',
        'quantum': 'QPU',
        'qpu': 'QPU'
    }
    
    # Filter to available modes in preferred order
    available_modes = [m for m in mode_order if m in modes]
    
    if len(available_modes) == 0:
        print("⚠ No modes to plot")
        return
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, len(available_modes), 
                             figsize=(5*len(available_modes), 6), 
                             sharey=True)
    
    # Handle single subplot case
    if len(available_modes) == 1:
        axes = [axes]
    
    # Colors for implementations
    colors = {'generic': '#FF6B6B', 'actual': '#4ECDC4'}
    markers = {'generic': 'o', 'actual': 's'}
    
    # Plot each mode
    for idx, mode in enumerate(available_modes):
        ax = axes[idx]
        mode_data = successful[successful['mode'] == mode]
        
        # Get all N values for this mode
        all_n_values = sorted(mode_data['N'].unique())
        
        # Plot both implementations
        for impl in ['generic', 'actual']:
            impl_data = mode_data[mode_data['implementation'] == impl]
            
            if len(impl_data) == 0:
                continue
            
            time_by_n = impl_data.groupby('N')['total_time'].mean().sort_index()
            
            ax.plot(time_by_n.index, time_by_n.values,
                   marker=markers[impl],
                   linestyle='-',
                   label=impl.capitalize(),
                   color=colors[impl],
                   markersize=10,
                   linewidth=2.5,
                   alpha=0.8)
        
        # Configure subplot
        ax.set_xticks(all_n_values)
        ax.set_xticklabels([str(n) for n in all_n_values], fontsize=11)
        ax.set_xlabel('N (number to factor)', fontsize=12)
        if idx == 0:
            ax.set_ylabel('Execution Time (seconds)', fontsize=12)
        
        mode_name = mode_names.get(mode, mode.upper())
        ax.set_title(mode_name, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.suptitle('Generic vs Actual Implementation Comparison', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = f'{output_dir}/implementation_comparison_combined.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Success rate vs shots with multiple lines for different configurations
def plot_shots_comparison(df, output_dir='plots'):
    """Plot success rate vs shots with separate lines for hardware modes and implementations."""
    Path(output_dir).mkdir(exist_ok=True)
    
    if 'shots' not in df.columns:
        print("⚠ Column 'shots' not found")
        return
    
    if df['shots'].nunique() < 2:
        print("⚠ Need multiple shot values to plot shots comparison")
        return
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 10))
    
    # Color schemes
    mode_colors = {
        'sim': 'red',
        'cpu': 'red',
        'parallel': 'darkred',
        'gpu': 'green',
        'quantum': 'blue',
        'qpu': 'blue'
    }
    
    impl_colors = {
        'generic': '#FF6B6B',
        'actual': '#4ECDC4'
    }
    
    mode_names = {
        'sim': 'CPU',
        'cpu': 'CPU',
        'parallel': 'Parallel',
        'gpu': 'GPU',
        'quantum': 'QPU',
        'qpu': 'QPU'
    }
    
    # Plot 1: By Hardware Mode
    ax1 = plt.subplot(2, 2, 1)
    if 'mode' in df.columns:
        for mode in sorted(df['mode'].unique()):
            mode_data = df[df['mode'] == mode]
            success_by_shots = mode_data.groupby('shots')['success'].agg(['sum', 'count'])
            success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
            
            color = mode_colors.get(mode, 'gray')
            label = mode_names.get(mode, mode.upper())
            
            ax1.plot(success_by_shots.index, success_by_shots['rate'],
                    marker='o', linestyle='-', label=label, color=color,
                    markersize=8, linewidth=2.5, alpha=0.8)
        
        ax1.set_xlabel('Number of Shots', fontsize=12)
        ax1.set_ylabel('Success Rate (%)', fontsize=12)
        ax1.set_title('Success Rate vs Shots (By Hardware)', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10, loc='best')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_ylim([0, 105])
    
    # Plot 2: By Implementation
    ax2 = plt.subplot(2, 2, 2)
    if 'implementation' in df.columns:
        for impl in sorted(df['implementation'].unique()):
            impl_data = df[df['implementation'] == impl]
            success_by_shots = impl_data.groupby('shots')['success'].agg(['sum', 'count'])
            success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
            
            color = impl_colors.get(impl, 'gray')
            marker = 'o' if impl == 'generic' else 's'
            
            ax2.plot(success_by_shots.index, success_by_shots['rate'],
                    marker=marker, linestyle='-', label=impl.capitalize(), color=color,
                    markersize=8, linewidth=2.5, alpha=0.8)
        
        ax2.set_xlabel('Number of Shots', fontsize=12)
        ax2.set_ylabel('Success Rate (%)', fontsize=12)
        ax2.set_title('Success Rate vs Shots (By Implementation)', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10, loc='best')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_ylim([0, 105])
    
    # Plot 3: By N value
    ax3 = plt.subplot(2, 2, 3)
    n_values = sorted(df['N'].unique())
    
    # Use a colormap for different N values
    cmap = plt.cm.get_cmap('tab10')
    
    for idx, n in enumerate(n_values):
        n_data = df[df['N'] == n]
        success_by_shots = n_data.groupby('shots')['success'].agg(['sum', 'count'])
        
        if len(success_by_shots) < 2:
            continue
            
        success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
        
        color = cmap(idx / len(n_values))
        
        ax3.plot(success_by_shots.index, success_by_shots['rate'],
                marker='o', linestyle='-', label=f'N={n}', color=color,
                markersize=8, linewidth=2.5, alpha=0.8)
    
    ax3.set_xlabel('Number of Shots', fontsize=12)
    ax3.set_ylabel('Success Rate (%)', fontsize=12)
    ax3.set_title('Success Rate vs Shots (By Problem Size)', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9, loc='best', ncol=2)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_ylim([0, 105])
    
    # Plot 4: Combined (Mode + Implementation)
    ax4 = plt.subplot(2, 2, 4)
    if 'mode' in df.columns and 'implementation' in df.columns:
        plotted_combos = []
        
        for mode in sorted(df['mode'].unique()):
            for impl in sorted(df['implementation'].unique()):
                combo_data = df[(df['mode'] == mode) & (df['implementation'] == impl)]
                
                if len(combo_data) == 0:
                    continue
                
                success_by_shots = combo_data.groupby('shots')['success'].agg(['sum', 'count'])
                
                if len(success_by_shots) < 2:
                    continue
                
                success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
                
                mode_name = mode_names.get(mode, mode.upper())
                label = f'{mode_name}/{impl.capitalize()}'
                
                # Combine colors
                base_color = mode_colors.get(mode, 'gray')
                linestyle = '-' if impl == 'generic' else '--'
                marker = 'o' if impl == 'generic' else 's'
                
                ax4.plot(success_by_shots.index, success_by_shots['rate'],
                        marker=marker, linestyle=linestyle, label=label, color=base_color,
                        markersize=7, linewidth=2, alpha=0.7)
                
                plotted_combos.append(label)
        
        ax4.set_xlabel('Number of Shots', fontsize=12)
        ax4.set_ylabel('Success Rate (%)', fontsize=12)
        ax4.set_title('Success Rate vs Shots (Mode + Implementation)', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=8, loc='best', ncol=2)
        ax4.grid(True, alpha=0.3, linestyle='--')
        ax4.set_ylim([0, 105])
    
    plt.suptitle('Success Rate vs Number of Shots - Comprehensive Comparison', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filename = f'{output_dir}/shots_comparison_comprehensive.png'
    plt.savefig(filename, dpi=300)
    print(f"✓ Saved: {filename}")
    plt.close()


# Alternative: Simpler single plot with all lines
def plot_shots_success_detailed(df, output_dir='plots'):
    """Single plot with all mode/implementation combinations."""
    Path(output_dir).mkdir(exist_ok=True)
    
    if 'shots' not in df.columns:
        print("⚠ Column 'shots' not found")
        return
    
    if df['shots'].nunique() < 2:
        print("⚠ Need multiple shot values to plot")
        return
    
    plt.figure(figsize=(12, 7))
    
    # Color and style mappings
    mode_colors = {
        'sim': 'red',
        'cpu': 'red',
        'parallel': 'darkred',
        'gpu': 'green',
        'quantum': 'blue',
        'qpu': 'blue'
    }
    
    mode_names = {
        'sim': 'CPU',
        'cpu': 'CPU',
        'parallel': 'Parallel',
        'gpu': 'GPU',
        'quantum': 'QPU',
        'qpu': 'QPU'
    }
    
    # Check what columns we have
    has_mode = 'mode' in df.columns
    has_impl = 'implementation' in df.columns
    
    if has_mode and has_impl:
        # Plot mode + implementation combinations
        for mode in sorted(df['mode'].unique()):
            for impl in sorted(df['implementation'].unique()):
                combo_data = df[(df['mode'] == mode) & (df['implementation'] == impl)]
                
                if len(combo_data) == 0:
                    continue
                
                success_by_shots = combo_data.groupby('shots')['success'].agg(['sum', 'count'])
                
                if len(success_by_shots) < 1:
                    continue
                
                success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
                
                mode_name = mode_names.get(mode, mode.upper())
                label = f'{mode_name} - {impl.capitalize()}'
                
                color = mode_colors.get(mode, 'gray')
                linestyle = '-' if impl == 'generic' else '--'
                marker = 'o' if impl == 'generic' else 's'
                
                plt.plot(success_by_shots.index, success_by_shots['rate'],
                        marker=marker, linestyle=linestyle, label=label, color=color,
                        markersize=8, linewidth=2.5, alpha=0.8)
    
    elif has_mode:
        # Plot just by mode
        for mode in sorted(df['mode'].unique()):
            mode_data = df[df['mode'] == mode]
            success_by_shots = mode_data.groupby('shots')['success'].agg(['sum', 'count'])
            success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
            
            color = mode_colors.get(mode, 'gray')
            label = mode_names.get(mode, mode.upper())
            
            plt.plot(success_by_shots.index, success_by_shots['rate'],
                    marker='o', linestyle='-', label=label, color=color,
                    markersize=8, linewidth=2.5, alpha=0.8)
    
    else:
        # Plot overall
        success_by_shots = df.groupby('shots')['success'].agg(['sum', 'count'])
        success_by_shots['rate'] = (success_by_shots['sum'] / success_by_shots['count']) * 100
        
        plt.plot(success_by_shots.index, success_by_shots['rate'],
                marker='o', linestyle='-', label='Overall', color='blue',
                markersize=8, linewidth=2.5, alpha=0.8)
    
    plt.xlabel('Number of Shots', fontsize=13)
    plt.ylabel('Success Rate (%)', fontsize=13)
    plt.title('Success Rate vs Number of Shots', fontsize=15, fontweight='bold')
    plt.legend(fontsize=10, loc='best', framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.ylim([0, 105])
    plt.tight_layout()
    
    filename = f'{output_dir}/shots_vs_success_detailed.png'
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
  python3 analyze.py --graphs implementation  # Only implementation comparison
  python3 analyze.py results/actual_sim_1/results.csv  # Analyze single file
        """
    )
    parser.add_argument('csv_file', nargs='?', help='CSV file with results (optional, auto-discovers if not provided)')
    parser.add_argument('--graphs', choices=['all', 'timing', 'scaling', 'success', 'hardware', 'implementation'], 
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
            plot_shots_comparison(df, args.output_dir)
            plot_shots_success_detailed(df, args.output_dir)
    
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
    
    if args.graphs in ['all', 'implementation']:
        plot_implementation_comparison(df, args.output_dir)
        plot_implementation_comparison_combined(df, args.output_dir)
    
    # Generate report
    generate_report(df, args.report)
    
    print(f"\n{'='*70}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'='*70}\n")
    print(f"Plots saved to: {args.output_dir}/")
    print(f"Report saved to: {args.report}")


if __name__ == '__main__':
    main()