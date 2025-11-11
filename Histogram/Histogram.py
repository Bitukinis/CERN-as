import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

# Read the CSV (first column)
df = pd.read_csv('data.csv')
data = df.iloc[:, 0]

# Count how many times each number appears
counts = data.value_counts().sort_index()

plt.figure(figsize=(10, 8))

# For each unique number, stack bubbles vertically
for i, num in enumerate(counts.index):
    freq = counts[num]
    y_positions = np.arange(1, freq + 1)
    
    # random colors for each bubble
    colors = [(random.random(), random.random(), random.random()) for _ in range(freq)]
    edge_colors = [(random.random(), random.random(), random.random()) for _ in range(freq)]
    
    plt.scatter([num] * freq, y_positions, s=400,
                color=colors, alpha=0.7, edgecolor=edge_colors, linewidth=2)

# --- Add a fit line through the top of each column ---
x = counts.index.values
y = counts.values

# Fit a simple polynomial (degree 2 for a smooth curve)
coeffs = np.polyfit(x, y, 2)
poly = np.poly1d(coeffs)
x_fit = np.linspace(min(x), max(x), 200)
y_fit = poly(x_fit)

plt.plot(x_fit, y_fit, color='red', linewidth=2, label='Fit Line')
plt.legend()

# --- Add total ball count text at the top ---
total_balls = len(data)
plt.text(0.5, max(y) + 0.8,
         f"Total bubbles: {total_balls}",
         ha='center', va='bottom', fontsize=12, color='darkblue', transform=plt.gca().transAxes)

# Labels and layout
plt.title('Stacked Bubble Histogram (Random Colors)')
plt.xlabel('Number')
plt.ylabel('Count')
plt.xticks(counts.index)
plt.yticks(range(1, max(counts.values) + 1))
plt.grid(alpha=0.3, linestyle=':')
plt.tight_layout()
plt.show()
