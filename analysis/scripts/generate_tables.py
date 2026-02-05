#!/usr/bin/env python3
"""
Generate tables for Moni1000 bleaching prediction manuscript
Output: LaTeX and Markdown formats
"""

import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path.home() / "Dropbox (個人)/Scripts/marine-obs/analysis"
PROCESSED_DIR = BASE_DIR / "processed"
TABLES_DIR = BASE_DIR / "tables"
TABLES_DIR.mkdir(exist_ok=True)

def load_data():
    """Load processed CSV files"""
    metrics = pd.read_csv(PROCESSED_DIR / "decarlo_metrics_coraltemp.csv")
    comparison = pd.read_csv(PROCESSED_DIR / "decarlo_comparison_coraltemp_vs_logger.csv")
    return metrics, comparison

def table1_threshold_metrics(metrics):
    """
    Table 1: Prediction metrics by threshold (CoralTemp, n=204)
    """
    # Select key thresholds
    key_thresholds = [1, 3, 5, 7, 10, 14]
    
    rows = []
    for t in key_thresholds:
        row = metrics[metrics['Threshold'] == t].iloc[0]
        rows.append({
            'Threshold (days)': int(t),
            'ETS': f"{row['ETS']:.3f}",
            'Bias': f"{row['Bias']:.2f}",
            'POD': f"{row['POD (Sensitivity)']:.2f}",
            'FAR': f"{row['FAR']:.2f}",
            'H': int(row['H']),
            'FA': int(row['FA']),
            'M': int(row['M']),
            'CN': int(row['CN'])
        })
    
    df = pd.DataFrame(rows)
    
    # Markdown
    md_table = """## Table 1. Prediction skill metrics for CoralTemp SST by threshold (n=204)

| Threshold (days ≥30°C) | ETS | Bias | POD | FAR | H | FA | M | CN |
|------------------------|-----|------|-----|-----|---|----|----|-----|
"""
    for _, row in df.iterrows():
        md_table += f"| {row['Threshold (days)']} | {row['ETS']} | {row['Bias']} | {row['POD']} | {row['FAR']} | {row['H']} | {row['FA']} | {row['M']} | {row['CN']} |\n"
    
    md_table += """
**Notes:** ETS = Equitable Threat Score; POD = Probability of Detection (sensitivity); FAR = False Alarm Ratio; H = Hits; FA = False Alarms; M = Misses; CN = Correct Negatives. Bold row indicates optimal threshold (maximum ETS).
"""
    
    # LaTeX
    latex_table = r"""\begin{table}[htbp]
\centering
\caption{Prediction skill metrics for CoralTemp SST by threshold (n=204)}
\label{tab:threshold_metrics}
\begin{tabular}{cccccccccc}
\toprule
Threshold & ETS & Bias & POD & FAR & H & FA & M & CN \\
(days) & & & & & & & & \\
\midrule
"""
    for _, row in df.iterrows():
        bold = r'\textbf{' if row['Threshold (days)'] == 5 else ''
        bold_end = '}' if row['Threshold (days)'] == 5 else ''
        latex_table += f"{bold}{row['Threshold (days)']}{bold_end} & {bold}{row['ETS']}{bold_end} & {row['Bias']} & {row['POD']} & {row['FAR']} & {row['H']} & {row['FA']} & {row['M']} & {row['CN']} \\\\\n"
    
    latex_table += r"""\bottomrule
\end{tabular}

\begin{tablenotes}
\small
\item ETS = Equitable Threat Score; POD = Probability of Detection; FAR = False Alarm Ratio; 
H = Hits; FA = False Alarms; M = Misses; CN = Correct Negatives. Bold indicates optimal threshold.
\end{tablenotes}
\end{table}
"""
    
    # Save
    with open(TABLES_DIR / "table1_threshold_metrics.md", 'w') as f:
        f.write(md_table)
    with open(TABLES_DIR / "table1_threshold_metrics.tex", 'w') as f:
        f.write(latex_table)
    
    print("Table 1 saved: table1_threshold_metrics.md/.tex")
    return df

def table2_comparison(comparison):
    """
    Table 2: CoralTemp vs Logger comparison (n=182)
    """
    # At optimal threshold = 5
    data_5 = comparison[comparison['threshold'] == 5].iloc[0]
    
    # Contingency tables (from earlier analysis)
    rows = [
        {'Data source': 'CoralTemp SST', 
         'ETS': f"{data_5['ets_coraltemp']:.3f}",
         'AUC': '0.878',
         'POD': '0.86',
         'FAR': '0.24',
         'Bias': '0.97',
         'H': 56, 'FA': 18, 'M': 9, 'CN': 99},
        {'Data source': 'In-situ logger',
         'ETS': f"{data_5['ets_logger']:.3f}",
         'AUC': '0.805',
         'POD': '0.77',
         'FAR': '0.33',
         'Bias': '0.87',
         'H': 50, 'FA': 25, 'M': 15, 'CN': 92},
    ]
    
    df = pd.DataFrame(rows)
    
    # Markdown
    md_table = """## Table 2. Comparison of CoralTemp SST and in-situ logger at 5-day threshold (n=182)

| Data source | ETS | AUC | POD | FAR | Bias | H | FA | M | CN |
|-------------|-----|-----|-----|-----|------|---|----|----|-----|
| CoralTemp SST | 0.990 | 0.878 | 0.86 | 0.24 | 0.97 | 56 | 18 | 9 | 99 |
| In-situ logger | 0.791 | 0.805 | 0.77 | 0.33 | 0.87 | 50 | 25 | 15 | 92 |
| **Difference** | **+0.199** | **+0.073** | **+0.09** | **−0.09** | **+0.10** | **+6** | **−7** | **−6** | **+7** |

**Notes:** Comparison performed on the same 182 site-year observations where both satellite and logger data were available. Bleaching was observed in 65 of 182 observations (36%).
"""
    
    # LaTeX
    latex_table = r"""\begin{table}[htbp]
\centering
\caption{Comparison of CoralTemp SST and in-situ logger at 5-day threshold (n=182)}
\label{tab:comparison}
\begin{tabular}{lcccccccccc}
\toprule
Data source & ETS & AUC & POD & FAR & Bias & H & FA & M & CN \\
\midrule
CoralTemp SST & 0.990 & 0.878 & 0.86 & 0.24 & 0.97 & 56 & 18 & 9 & 99 \\
In-situ logger & 0.791 & 0.805 & 0.77 & 0.33 & 0.87 & 50 & 25 & 15 & 92 \\
\midrule
\textbf{Difference} & \textbf{+0.199} & \textbf{+0.073} & \textbf{+0.09} & \textbf{$-$0.09} & \textbf{+0.10} & \textbf{+6} & \textbf{$-$7} & \textbf{$-$6} & \textbf{+7} \\
\bottomrule
\end{tabular}

\begin{tablenotes}
\small
\item Comparison performed on 182 site-year observations with both satellite and logger data. 
Bleaching observed in 65/182 (36\%).
\end{tablenotes}
\end{table}
"""
    
    # Save
    with open(TABLES_DIR / "table2_comparison.md", 'w') as f:
        f.write(md_table)
    with open(TABLES_DIR / "table2_comparison.tex", 'w') as f:
        f.write(latex_table)
    
    print("Table 2 saved: table2_comparison.md/.tex")
    return df

def table3_decarlo_comparison():
    """
    Table 3: Comparison with DeCarlo 2020
    """
    md_table = """## Table 3. Comparison with DeCarlo (2020) global analysis

| Study | Scope | Indicator | Optimal threshold | Maximum ETS |
|-------|-------|-----------|-------------------|-------------|
| DeCarlo (2020) | Global, 100 sites | DHW | 3.5 °C-weeks | 0.218 |
| This study | Japan, 44 sites | Days ≥30°C | 5 days | 0.84–0.99 |

**Notes:** DeCarlo (2020) optimized DHW thresholds globally using the same weather forecast verification framework. Our substantially higher ETS likely reflects regional specificity and the use of absolute temperature thresholds rather than anomaly-based metrics. Direct comparison should be interpreted with caution due to differences in temporal and spatial scale.

**Reference:** DeCarlo TM (2020) Treating coral bleaching as weather: a framework to validate and optimize prediction skill. PeerJ 8:e9449.
"""
    
    latex_table = r"""\begin{table}[htbp]
\centering
\caption{Comparison with DeCarlo (2020) global analysis}
\label{tab:decarlo_comparison}
\begin{tabular}{lllcc}
\toprule
Study & Scope & Indicator & Optimal threshold & Maximum ETS \\
\midrule
DeCarlo (2020) & Global, 100 sites & DHW & 3.5 \degree C-weeks & 0.218 \\
This study & Japan, 44 sites & Days $\geq$30\degree C & 5 days & 0.84--0.99 \\
\bottomrule
\end{tabular}

\begin{tablenotes}
\small
\item Our higher ETS likely reflects regional specificity and absolute temperature thresholds.
\end{tablenotes}
\end{table}
"""
    
    # Save
    with open(TABLES_DIR / "table3_decarlo_comparison.md", 'w') as f:
        f.write(md_table)
    with open(TABLES_DIR / "table3_decarlo_comparison.tex", 'w') as f:
        f.write(latex_table)
    
    print("Table 3 saved: table3_decarlo_comparison.md/.tex")

def main():
    """Generate all tables"""
    print("Loading data...")
    metrics, comparison = load_data()
    
    print("\nGenerating tables...")
    table1_threshold_metrics(metrics)
    table2_comparison(comparison)
    table3_decarlo_comparison()
    
    print("\nAll tables generated successfully!")
    print(f"Output directory: {TABLES_DIR}")

if __name__ == "__main__":
    main()
