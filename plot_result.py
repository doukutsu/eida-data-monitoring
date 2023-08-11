import json
import argparse
import glob
import copy
import statistics
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from cartopy.io.img_tiles import GoogleTiles
import cartopy.crs as ccrs
import numpy as np
import urllib.request

def plot_map(xs,ys,cs,xm,ym,extent,detail,outfile):
  plt.ioff()
  tiler = GoogleTiles(style='satellite')
  fig = plt.figure(figsize=(10, 7.5))
  ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
  N = 128
  vals = np.ones((2*N, 4))
  vals[:, 0] = np.concatenate((np.linspace(255/255, 255/255, N),np.linspace(255/255,   0/255, N)))
  vals[:, 1] = np.concatenate((np.linspace(  0/255, 181/255, N),np.linspace(181/255, 255/255, N)))
  vals[:, 2] = np.concatenate((np.linspace(  0/255, 197/255, N),np.linspace(197/255,   0/255, N)))
  newcmp = ListedColormap(vals)
  ax.scatter(xm, ym, transform=ccrs.PlateCarree(),
             marker='^', color='#ffffff', s=10,
             linewidths=0.12,edgecolor='#707070',
             zorder=2, label='not available during test')
  sc = ax.scatter(xs, ys, transform=ccrs.PlateCarree(),
             marker='^', c=cs, s=12,
             linewidths=0.12,edgecolor='#000000',
             cmap=newcmp,zorder=3,
             norm=plt.Normalize(min(cs),max(cs)))
  ax.legend(loc='lower left',bbox_to_anchor=(0.0,-0.084),framealpha=1.0,facecolor='#060606',labelcolor='#f1f1f1',edgecolor='#060606')
  ax.add_image(tiler, detail,zorder=1)
  ax.set_extent(extend, ccrs.PlateCarree())
  plt.colorbar(sc,location='bottom',label='retrievability [%]',shrink=0.33,anchor=(0.72,2.11))
  plt.savefig(outfile,dpi=400,bbox_inches="tight")
  plt.close()

def inv_recurse(total,key,item):
  if type(item) is dict:
    if not key in total:
      total[key] = {}
    for rkey,ritem in item.items():
      inv_recurse(total[key],rkey,ritem)
  else:
    if not key in total:
      total[key] = [min([1.0,item])]
    else:
      total[key].append(min([1.0,item]))

def main():
  with open('coordinates.json') as coordsfile:
    coords = json.load(coordsfile)
  results = []
  for index,infile in enumerate(glob.glob('./results*.json')):
    with open(infile) as jsonfile:
      results.append(json.load(jsonfile))
  comb = {}
  for result in results:
    for nodekey,nodeval in result.items():
      inv_recurse(comb,nodekey,nodeval)
  xs = []
  ys = []
  cs = []
  for nodekey,nodeval in comb.items():
    for yearkey,yearval in nodeval.items():
      for netkey,netval in yearval.items():
        for stakey,staval in netval.items():
          for chakey,chaval in staval.items():
            for finkey,finval in chaval.copy().items():
              if finkey == 'percentage':
                if netkey in coords:
                  if stakey in coords[netkey]:
                    xs.append(coords[netkey][stakey]['longitude'])
                    ys.append(coords[netkey][stakey]['latitude'])
                    cs.append(sum(comb[nodekey][yearkey][netkey][stakey][chakey][finkey])/len(results)*100)
                  else:
                    print('Failed to find coordinate information for %s %s.' % (netkey,stakey))
                else:
                  print('Failed to find coordinate information for %s.' % (netkey))
  xm = []
  ym = []
  for netkey,netval in coords.items():
    for stakey,staval in netval.items():
      xm.append(staval['longitude'])
      ym.append(staval['latitude'])
  plot_map(xs,ys,cs,xm,ym,[-20, 46, 27.4, 76],7,'retrievability_europe.png')
  plot_map(xs,ys,cs,xm,ym,[-180, 180, -90, 90],5,'retrievability_global.png')
  print('DONE!')

if __name__ == '__main__':
  main()
