#!/usr/bin/env python3
"""
Generate figures for Moni1000 bleaching prediction manuscript
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Paths
BASE_DIR = Path.home() / "Dropbox (個人)/Scripts/marine-obs/analysis"
PROCESSED_DIR = BASE_DIR / "processed"
FIGURES_DIR = BASE_DIR / "figures"

# Style settings
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# Colors
COLOR_CORALTEMP = '#1f77b4'  # Blue
COLOR_LOGGER = '#ff7f0e'     # Orange
COLOR_DECARLO = '#2ca02c'    # Green

def load_data():
    """Load processed CSV files"""
    metrics = pd.read_csv(PROCESSED_DIR / "decarlo_metrics_coraltemp.csv")
    comparison = pd.read_csv(PROCESSED_DIR / "decarlo_comparison_coraltemp_vs_logger.csv")
    return metrics, comparison

def figure1_ets_by_threshold(metrics, comparison):
    """
    Figure 1: ETS by threshold (CoralTemp vs Logger)
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # CoralTemp (full dataset n=204)
    ax.plot(metrics['Threshold'], metrics['ETS'], 
            'o-', color=COLOR_CORALTEMP, linewidth=2, markersize=6,
            label=f'CoralTemp (n=204)')
    
    # Logger comparison points (n=182)
    ax.plot(comparison['threshold'], comparison['ets_logger'],
            's--', color=COLOR_LOGGER, linewidth=2, markersize=8,
            label=f'In-situ logger (n=182)')
    
    # CoralTemp at same thresholds as comparison
    ax.plot(comparison['threshold'], comparison['ets_coraltemp'],
            'o-', color=COLOR_CORALTEMP, linewidth=2, markersize=8,
            alpha=0.5)
    
    # Highlight optimal threshold
    optimal_idx = metrics['ETS'].idxmax()
    optimal_threshold = metrics.loc[optimal_idx, 'Threshold']
    optimal_ets = metrics.loc[optimal_idx, 'ETS']
    ax.axvline(x=optimal_threshold, color='gray', linestyle=':', alpha=0.7)
    ax.annotate(f'Optimal: {optimal_threshold} days\nETS={optimal_ets:.2f}',
                xy=(optimal_threshold, optimal_ets),
                xytext=(optimal_threshold + 3, optimal_ets - 0.1),
                fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.7))
    
    # DeCarlo 2020 reference line
    ax.axhline(y=0.218, color=COLOR_DECARLO, linestyle='--', alpha=0.7)
    ax.annotate('DeCarlo 2020 global optimum (0.218)',
                xy=(15, 0.218), xytext=(15, 0.28),
                fontsize=9, color=COLOR_DECARLO,
                arrowprops=dict(arrowstyle='->', color=COLOR_DECARLO, alpha=0.7))
    
    ax.set_xlabel('Threshold (days ≥30°C)', fontsize=12)
    ax.set_ylabel('Equitable Threat Score (ETS)', fontsize=12)
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(0, 1.05)
    ax.legend(loc='upper right', frameon=False)
    ax.set_title('A. Prediction skill by threshold', fontsize=13, fontweight='bold', loc='left')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_ets_threshold.png", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "fig1_ets_threshold.pdf", bbox_inches='tight')
    print("Figure 1 saved: fig1_ets_threshold.png/pdf")
    plt.close()

def figure2_roc_curve(metrics):
    """
    Figure 2: ROC curve for CoralTemp
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Calculate FPR and TPR
    fpr = 1 - metrics['Specificity']
    tpr = metrics['POD (Sensitivity)']
    
    # Plot ROC curve
    ax.plot(fpr, tpr, 'o-', color=COLOR_CORALTEMP, linewidth=2, markersize=5)
    
    # Annotate key thresholds
    for idx in [0, 5, 10, 15, 20]:
        if idx < len(metrics):
            ax.annotate(f'{idx}d', 
                       (fpr.iloc[idx], tpr.iloc[idx]),
                       textcoords="offset points", xytext=(5, 5),
                       fontsize=8, alpha=0.7)
    
    # Diagonal reference line
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Random classifier')
    
    # AUC annotation
    # Calculate AUC using trapezoidal rule
    sorted_idx = np.argsort(fpr)
    auc = np.trapz(tpr.iloc[sorted_idx], fpr.iloc[sorted_idx])
    ax.annotate(f'AUC = {abs(auc):.2f}', xy=(0.6, 0.3), fontsize=12)
    
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect('equal')
    ax.set_title('B. ROC curve (CoralTemp)', fontsize=13, fontweight='bold', loc='left')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_roc_curve.png", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "fig2_roc_curve.pdf", bbox_inches='tight')
    print("Figure 2 saved: fig2_roc_curve.png/pdf")
    plt.close()

def figure3_comparison_bar(comparison):
    """
    Figure 3: CoralTemp vs Logger comparison at optimal threshold
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Data at threshold = 5
    data_5 = comparison[comparison['threshold'] == 5].iloc[0]
    
    metrics_names = ['ETS', 'POD', '1-FAR']
    coraltemp_vals = [data_5['ets_coraltemp'], 0.86, 1-0.24]  # From paper
    logger_vals = [data_5['ets_logger'], 0.77, 1-0.33]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, coraltemp_vals, width, label='CoralTemp', color=COLOR_CORALTEMP)
    bars2 = ax.bar(x + width/2, logger_vals, width, label='In-situ logger', color=COLOR_LOGGER)
    
    # Add value labels
    for bar, val in zip(bars1, coraltemp_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, logger_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', frameon=False)
    ax.set_title('C. Satellite vs in-situ at 5-day threshold (n=182)', 
                fontsize=13, fontweight='bold', loc='left')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig3_comparison_bar.png", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "fig3_comparison_bar.pdf", bbox_inches='tight')
    print("Figure 3 saved: fig3_comparison_bar.png/pdf")
    plt.close()

def figure_combined():
    """
    Combined figure for manuscript (2-panel or 3-panel)
    """
    metrics, comparison = load_data()
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Panel A: ETS by threshold
    ax = axes[0]
    ax.plot(metrics['Threshold'], metrics['ETS'], 
            'o-', color=COLOR_CORALTEMP, linewidth=2, markersize=6,
            label='CoralTemp (n=204)')
    ax.plot(comparison['threshold'], comparison['ets_logger'],
            's--', color=COLOR_LOGGER, linewidth=2, markersize=8,
            label='In-situ logger (n=182)')
    
    # Highlight optimal
    optimal_idx = metrics['ETS'].idxmax()
    optimal_threshold = metrics.loc[optimal_idx, 'Threshold']
    optimal_ets = metrics.loc[optimal_idx, 'ETS']
    ax.axvline(x=optimal_threshold, color='gray', linestyle=':', alpha=0.7)
    
    # DeCarlo reference
    ax.axhline(y=0.218, color=COLOR_DECARLO, linestyle='--', alpha=0.7, label='DeCarlo 2020 (0.218)')
    
    ax.set_xlabel('Threshold (days ≥30°C)', fontsize=12)
    ax.set_ylabel('Equitable Threat Score (ETS)', fontsize=12)
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(0, 1.05)
    ax.legend(loc='upper right', frameon=False, fontsize=10)
    ax.set_title('A', fontsize=14, fontweight='bold', loc='left')
    
    # Panel B: Comparison bar
    ax = axes[1]
    data_5 = comparison[comparison['threshold'] == 5].iloc[0]
    metrics_names = ['ETS', 'POD', '1-FAR']
    coraltemp_vals = [data_5['ets_coraltemp'], 0.86, 1-0.24]
    logger_vals = [data_5['ets_logger'], 0.77, 1-0.33]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    bars1 = ax.bar(x - width/2, coraltemp_vals, width, label='CoralTemp', color=COLOR_CORALTEMP)
    bars2 = ax.bar(x + width/2, logger_vals, width, label='In-situ logger', color=COLOR_LOGGER)
    
    for bar, val in zip(bars1, coraltemp_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, logger_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right', frameon=False, fontsize=10)
    ax.set_title('B', fontsize=14, fontweight='bold', loc='left')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig_combined.png", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "fig_combined.pdf", bbox_inches='tight')
    print("Combined figure saved: fig_combined.png/pdf")
    plt.close()

def main():
    """Generate all figures"""
    print("Loading data...")
    metrics, comparison = load_data()
    print(f"Metrics: {len(metrics)} rows")
    print(f"Comparison: {len(comparison)} rows")
    
    print("\nGenerating figures...")
    figure1_ets_by_threshold(metrics, comparison)
    figure2_roc_curve(metrics)
    figure3_comparison_bar(comparison)
    figure_combined()
    
    print("\nAll figures generated successfully!")
    print(f"Output directory: {FIGURES_DIR}")

if __name__ == "__main__":
    main()
