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
  args = parser.parse_args()
  station_dictionary = {}
  output_text = []
  start_year = UTCDateTime(args.start,1,1)
  end_year = UTCDateTime(args.end,12,31)
  inv = RoutingClient("eida-routing").get_stations(
    channel = '*HZ',
    starttime = start_year,
    endtime = end_year,
    level = 'station',
    includerestricted = False,
  )
  append_dictionary(station_dictionary,inv)
  with open('coordinates.json','w') as outfile:
    json.dump(station_dictionary,outfile)

if __name__ == '__main__':
  main()
