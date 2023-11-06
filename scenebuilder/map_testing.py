import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Suppose this is your existing figure and axis with some plot
fig, ax = plt.subplots()
ax.plot([0, 1, 2, 3], [0, 1, 0, 1], 'r-')

# Create a Basemap instance tied to that axis
m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=ax)

m.drawcoastlines()
m.drawcountries()
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='coral',lake_color='aqua')

# To make sure the original plot remains on top
ax.plot([0, 1, 2, 3], [0, 1, 0, 1], 'r-')

plt.show()
