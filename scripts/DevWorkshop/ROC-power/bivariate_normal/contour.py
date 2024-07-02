import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, multivariate_normal

epsi = 1e-6
n_points = 1000
x_ori = np.linspace(epsi, 1-epsi, n_points)
x = norm.ppf(x_ori)
X, Y = np.meshgrid(x,x)
XY = np.array([[(X[i,j], Y[i,j]) for i in range(n_points)] for j in range(n_points)])

mean = [0, 0]
covariance = [[1, 0.5], [0.5, 1]]
bivariate_normal = multivariate_normal(mean=mean, cov=covariance)
Z = bivariate_normal.pdf(XY)

X_ori, Y_ori = np.meshgrid(x_ori, x_ori)

plt.contourf(X_ori, Y_ori, Z, levels=20, cmap='viridis')  # Filled contour plot
plt.colorbar()  # Add a colorbar
plt.title('Contour Plot')
plt.xlabel('X axis')
plt.ylabel('Y axis')

# Step 4: Display the plot
plt.show()