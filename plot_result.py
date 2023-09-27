import json
import argparse
import glob
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.offsetbox import AnchoredText
from cartopy.io.img_tiles import GoogleTiles
import cartopy.crs as ccrs
import numpy as np

def plot_map(xs,ys,cs,xm,ym,xp,yp,extent,detail,outfile):
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
  ax.scatter(xp, yp, transform=ccrs.PlateCarree(),
             marker='^', color='#ff70ff', s=10,
             linewidths=0.12,edgecolor='#70ff70',
             zorder=5, label='metadata problem')
  sc = ax.scatter(xs, ys, transform=ccrs.PlateCarree(),
             marker='^', c=cs, s=12,
             linewidths=0.12,edgecolor='#000000',
             cmap=newcmp,zorder=3,
             norm=plt.Normalize(min(cs),max(cs)))
  ax.legend(loc='upper left',bbox_to_anchor=(0.0,0.005),
            framealpha=1.0,facecolor='#060606',
            labelcolor='#f1f1f1',edgecolor='#060606')
  ax.add_image(tiler, detail,zorder=1)
  ax.set_extent(extent, ccrs.PlateCarree())
  text = AnchoredText('Images \u00A9 2023 TerraMetrics, Map Data \u00A9 2023 Google',
                      loc=4, prop={'size': 12}, frameon=True)
  ax.add_artist(text)
  plt.colorbar(sc,location='bottom',label='retrievability [%]',
               shrink=0.33,anchor=(0.72,2.11))
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
  desc = 'Script to plot station maps for the results of the EIDA data retrievability tests.'
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('-c', '--coords_filename', default="coordinates.json", type=str,
                      help='Name of the file containing the station coordinates information (default="coordinates.json").')
  parser.add_argument('-g', '--global_overview_map', default=True, type=bool,
                      help='Switch for plotting the global overview map (default=True).')
  parser.add_argument('-o', '--output_filename', default="retrievability", type=str,
                      help='Filename to write the results to (default="retrievability").')
  parser.add_argument('-r', '--results_directory', default=".", type=str,
                      help='Directory with the result files (default=".").')
  parser.add_argument('-t', '--type', default='ret', type=str,
                      help='Type of the result to plot (actual retrievability (ret) or waveform catalogue info (wfc)) (default=ret).')
  args = parser.parse_args()
  print('Plotting %s map...' % 'retrievability' if args.type == 'ret' else 'waveform catalogue')
  with open(args.coords_filename) as coordsfile:
    coords = json.load(coordsfile)
  results = []
  for _,infile in enumerate(glob.glob(args.results_directory+'/results*.json')):
    with open(infile) as jsonfile:
      results.append(json.load(jsonfile))
  comb = {}
  for result in results:
    for nodekey,nodeval in result.items():
      inv_recurse(comb,nodekey,nodeval)
  xs = []
  ys = []
  cs = []
  xp = []
  yp = []
  key = 'percentage' if args.type == 'ret' else 'days_with_metrics'
  for _,nodeval in comb.items():
    for _,yearval in nodeval.items():
      for netkey,netval in yearval.items():
        for stakey,staval in netval.items():
          for _,chaval in staval.items():
            for finkey,finval in chaval.items():
              if netkey in coords:
                if stakey in coords[netkey]:
                  if finkey == key:
                    xs.append(coords[netkey][stakey]['longitude'])
                    ys.append(coords[netkey][stakey]['latitude'])
                    cs.append(sum(finval)/len(results)*100)
                  elif finkey == 'metadata_problem' and all(finval):
                    xp.append(coords[netkey][stakey]['longitude'])
                    yp.append(coords[netkey][stakey]['latitude'])
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
  plot_map(xs,ys,cs,xm,ym,xp,yp,[-20, 46, 27.4, 76],7,args.output_filename+'_europe.png')
  if args.global_overview_map:
    plot_map(xs,ys,cs,xm,ym,xp,yp,[-180, 180, -90, 90],5,args.output_filename+'_global.png')
  print('DONE!')

if __name__ == '__main__':
  main()
