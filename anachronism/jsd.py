## Refrence implementation generated by Claude

import numpy as np
from scipy.spatial import distance
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

def calculate_js_divergence(data1, data2, num_points=1000):
    # Create kernel density estimates
    kde1 = gaussian_kde(data1)
    kde2 = gaussian_kde(data2)
    
    # Create a common evaluation grid
    x_min = min(data1.min(), data2.min())
    x_max = max(data1.max(), data2.max())
    x_grid = np.linspace(x_min, x_max, num_points)
    
    # Calculate probability densities on the grid
    p = kde1(x_grid)
    q = kde2(x_grid)
    
    # Normalize to ensure they're proper probability distributions
    p = p / np.sum(p)
    q = q / np.sum(q)
    
    # Calculate Jensen-Shannon divergence
    js_divergence = distance.jensenshannon(p, q)
    
    return js_divergence

# Example usage
np.random.seed(42)
data1 = np.random.normal(0, 1, 1000)  # Normal distribution with mean 0, std 1
data2 = np.random.normal(0.5, 1.2, 1000)  # Slightly different normal distribution

js_div = calculate_js_divergence(data1, data2)
print(f"Jensen-Shannon Divergence: {js_div}")

# Visualize the two distributions
plt.figure(figsize=(10, 6))
x = np.linspace(-4, 6, 1000)
kde1 = gaussian_kde(data1)
kde2 = gaussian_kde(data2)

plt.plot(x, kde1(x), label='Distribution 1')
plt.plot(x, kde2(x), label='Distribution 2')
plt.title(f'KDE Plots with JS Divergence: {js_div:.4f}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()