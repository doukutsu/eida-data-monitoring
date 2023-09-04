import os
import json
import argparse
import datetime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn import RoutingClient
from obspy import UTCDateTime

def append_dictionary(station_dictionary, inv):
  for network in inv:
    if network.code not in station_dictionary:
      station_dictionary[network.code] = {}
    for station in network:
      if station.code not in station_dictionary[network.code]:
        station_dictionary[network.code][station.code] = {
          "latitude" : station.latitude,
          "longitude" : station.longitude,
          "elevation" : station.elevation,
        }

def main():
  sy = datetime.datetime.now().year - 1
  ey = sy
  desc = 'Script to create a list of station coordinates.'
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('-s', '--start', default=sy, type=int,
                      help='Year to start the test (default=last year).')
  parser.add_argument('-e', '--end', default=ey, type=int,
                      help='Year to end the test (default=last year).')
  parser.add_argument('-r', '--eida_routing', default=True, type=bool,
                      help='Switch to choose between eida routing and individual node clients (default=True).')
  parser.add_argument('-a', '--authentication', default=os.path.expanduser('~/.eidatoken'),
                      help='File containing the token to use during the authentication process (default=~/.eidatoken).')
  parser.add_argument('-t', '--timeout', default=30, type=int,
                      help='Number of seconds to be used as a timeout for the HTTP calls (default=30).')
  args = parser.parse_args()
  token = args.authentication
  start_year = UTCDateTime(args.start,1,1)
  end_year = UTCDateTime(args.end,12,31)
  if args.eida_routing:
    eida_nodes = ["eida-routing"]
  else:
    eida_nodes = [ "http://eida.geo.uib.no", "GFZ", "RESIF", "INGV", "ETH", "BGR", "NIEP", "KOERI", "LMU", "NOA", "ICGC", "ODC" ]
  station_dictionary = {}
  for node in eida_nodes:
    print("Initializing "+node+" client.")
    try:
      if args.eida_routing:
        rsClient = RoutingClient("eida-routing",timeout=args.timeout,credentials={'EIDA_TOKEN': token})
      else:
        rsClient = Client(base_url=node,timeout=args.timeout,eida_token=token)
    except:
      print("*!!!* Failed to initialize client with eida token, proceeding without authentication. *!!!*")
      if args.eida_routing:
        rsClient = RoutingClient("eida-routing",timeout=args.timeout)
      else:
        rsClient = Client(base_url=node,timeout=args.timeout)
    print('Downloading station inventory...')
    inv = rsClient.get_stations(
      channel = '*HZ',
      starttime = start_year,
      endtime = end_year,
      level = 'station',
      includerestricted = False,
    )
    append_dictionary(station_dictionary,inv)
  print('Writing "coordinates.json"...')
  with open('coordinates.json','w') as outfile:
    json.dump(station_dictionary,outfile)
  print("Done.")

if __name__ == '__main__':
  main()
