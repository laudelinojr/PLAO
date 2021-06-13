import matplotlib
#import matplotlib.__version__
import numpy as np
import matplotlib.pyplot as plt

#tempo mínimo e máximo do eperimento (X)
t = np.arange(1, 30, 1)

#percentual maximo e minimo em (Y)
s = np.sin(2 * np.pi * t)

fig, ax = plt.subplots()

ax.plot(t, s)
# Thick red horizontal line at y=0 that spans the xrange.
ax.axhline(linewidth=8, color='#d62728')
# Horizontal line at y=1 that spans the xrange.
ax.axhline(y=1)
# Vertical line at x=1 that spans the yrange.
ax.axvline(x=1)
# Thick blue vertical line at x=0 that spans the upper quadrant of the yrange.
ax.axvline(x=0, ymin=0.75, linewidth=8, color='#1f77b4')
# Default hline at y=.5 that spans the middle half of the axes.
ax.axhline(y=.5, xmin=0.25, xmax=0.75)
# Infinite black line going through (0, 0) to (1, 1).
ax.axline((0, 0), (1, 1), color='k')
# 50%-gray rectangle spanning the axes' width from y=0.25 to y=0.75.
ax.axhspan(0.25, 0.75, facecolor='0.5')
# Green rectangle spanning the axes' height from x=1.25 to x=1.55.
ax.axvspan(3.00, 3.30, facecolor='#2ca02c')
ax.axvspan(6.00, 6.30, facecolor='#2ca02c')

plt.show()
fig.canvas.get_supported_filetypes()

#https://minerandodados.com.br/analise-de-dados-com-python-usando-pandas/#:~:text=O%20Pandas%20%C3%A9%20uma%20biblioteca,%2Cexcel%2Ctxt%2Cetc.