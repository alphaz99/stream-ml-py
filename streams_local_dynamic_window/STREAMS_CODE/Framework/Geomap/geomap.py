import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


class Geomap:
    def __init__(self, llcrnrlat, llcrnrlon, urcrnrlat, urcrnrlon,
                 projection='cyl', resolution='l', area_thresh=1000.0,
                 figsize=(15, 8)):
        self.llcrnrlat = llcrnrlat
        self.llcrnrlon = llcrnrlon
        self.urcrnrlat = urcrnrlat
        self.urcrnrlon = urcrnrlon
        self.projection = projection
        self.resolution = resolution
        self.area_thresh = area_thresh
        self.initialize(figsize)

    def initialize(self, figsize):
        plt.ion()
        self.map = Basemap(projection=self.projection,
                           llcrnrlat=self.llcrnrlat,
                           llcrnrlon=self.llcrnrlon, urcrnrlat=self.urcrnrlat,
                           urcrnrlon=self.urcrnrlon,
                           resolution=self.resolution,
                           area_thresh=self.area_thresh)
        self.f = plt.figure(figsize=figsize)
        self.draw_map()
        self.f.tight_layout()
        self.pt_sets = []

    def draw_map(self):
        self.map.drawcoastlines()
        self.map.drawcountries()
        self.map.drawstates()
        self.map.fillcontinents(color='gainsboro', lake_color='grey')
        self.map.drawmapboundary(fill_color='grey')

    def plot(self, x, index=None, text=None, color='Blue', s=30):
        lat = x[:, 0]
        lon = x[:, 1]
        x_map, y_map = self.map(lon, lat)
        if index is None:
            c = color
        else:
            c = index
        rainbow = plt.get_cmap('rainbow')
        p = self.map.scatter(x_map, y_map, c=c, cmap=rainbow, s=s, zorder=2)
        self.pt_sets.append(p)
        if text is not None:
            for i in range(0, len(x)):
                p = plt.annotate(text[i][0], xy=(x_map[i], y_map[i]),
                                 xytext=(x_map[i] + 0.5, y_map[i] + 0.5),
                                 fontsize=10,
                                 bbox={'facecolor': 'white', 'alpha': 0.5})
                self.pt_sets.append(p)
        plt.draw()

    def clear(self):
        for p in self.pt_sets[:]:
            p.remove()
            self.pt_sets.remove(p)
