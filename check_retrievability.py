"""Test for the User Advisory Group to monitor Data Availability within EIDA.

   Johannes Stampa <johannes.stampa@ifg.uni-kiel.de>, Christian-Albrechts-Universität Kiel

   based on a script by Florian Fuchs <florian.fuchs@univie.ac.at>, Univ. Vienna, Austria
"""

import os
import json
import argparse
import datetime
import random
import time
import requests
import json
from obspy.clients.fdsn import Client
from obspy.clients.fdsn import RoutingClient
from obspy import UTCDateTime
from obspy import Stream

def wfcatalog(net, sta, cha, start, end):
  params = dict()
  params['network'] = net
  params['station'] = sta
  params['channel'] = cha
  # No time can be included in these parameters because the WFCatalog
  # at BGR seems to have problems with it
  params['start'] = '%d-%02d-%02d' % (start.year, start.month, start.day)
  params['end'] = '%d-%02d-%02d' % (end.year, end.month, end.day)
  params['format'] = 'post'
  params['service'] = 'wfcatalog'
  r = requests.get('http://www.orfeus-eu.org/eidaws/routing/1/query', params)
  if r.status_code == 200:
    wfcurl = r.content.decode('utf-8').splitlines()[0]
  else:
    raise Exception('No routing information for WFCatalog: %s' % params)
  del params['format']
  del params['service']
  params['include'] = 'sample'
  params['longestonly'] = 'false'
  params['minimumlength'] = 0.0
  r = requests.get(wfcurl, params)
  if r.status_code == 200:
    metrics = json.loads(r.content.decode('utf-8'))
  else:
    raise Exception('No metrics for %s.%s %s' % (net, sta, start))
  return metrics

def main():
  # Default values for start and end time (last year)
  sy = datetime.datetime.now().year - 1
  ey = sy
  desc = 'Script to check accessibility of data through all EIDA nodes.'
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('-s', '--start', default=sy, type=int,
                      help='Year to start the test (default=last year).')
  parser.add_argument('-e', '--end', default=ey, type=int,
                      help='Year to end the test (default=last year).')
  parser.add_argument('--days', default=5, type=int,
                      help='How many days to randomly pick from the year (default=5).')
  parser.add_argument('--hours', default=2, type=int,
                      help='How many hours to randomly pick from each day (default=2).')
  parser.add_argument('--minutes', default=10, type=int,
                      help='Length of each individual download request in minutes (default=10).')
  parser.add_argument('-t', '--timeout', default=30, type=int,
                      help='Number of seconds to be used as a timeout for the HTTP calls (default=30).')
  parser.add_argument('-x', '--exclude', default=None,
                      help='List of comma-separated networks to be excluded from this test (e.g. XX,YY,ZZ).')
  parser.add_argument('-a', '--authentication', default=os.path.expanduser('~/.eidatoken'),
                      help='File containing the token to use during the authentication process (default=~/.eidatoken).')
  parser.add_argument('--start_month', default=1, type=int,
                      help='Month to start the test (default=1).')
  parser.add_argument('--end_month', default=12, type=int,
                      help='Month to end the test (default=12).')
  parser.add_argument('--start_day', default=1, type=int,
                      help='Day of the month to start the test (default=1).')
  parser.add_argument('--end_day', default=31, type=int,
                      help='Day of the month to end the test (default=31).')
  parser.add_argument('-r', '--eida_routing', default=True, type=bool,
                      help='Switch to choose between eida routing and individual node clients (default=True).')
  parser.add_argument('-o', '--output_filename', default="results.json", type=str,
                      help='Filename to write the results to (default="results.json").')
  args = parser.parse_args()
  # List of networks to exclude
  if args.exclude is not None:
    nets2exclude = list(map(str.strip, args.exclude.split(',')))
  else:
    nets2exclude = list()
  # Create a client to the EIDA Routing Service
  token = args.authentication
  if args.eida_routing:
   eida_nodes = ["eida-routing"]
  else:
   eida_nodes = [ "http://eida.geo.uib.no", "GFZ", "RESIF", "INGV", "ETH", "BGR", "NIEP", "KOERI", "LMU", "NOA", "ICGC", "ODC" ]
  results = {}
  for node in eida_nodes:
    results[node] = {}
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
    years = range(args.start, args.end+1)
    for index,y in enumerate(years):
      results[node][y] = {}
      print('Processing year %d' % y)
      if index == 0:
        t0 = UTCDateTime(y, args.start_month, args.start_day)
      else:
        t0 = UTCDateTime(y, 1, 1)
      if index == len(years)-1:
        t1 = UTCDateTime(y, args.end_month, args.end_day)
      else:
        t1 = UTCDateTime(y, 12, 31, 23, 59, 59)
      # Do not include restricted streams
      try:
        st = rsClient.get_stations(level='channel', channel='BHZ,HHZ', starttime=t0, endtime=t1,
                      includerestricted=False)
        totchannels = len(st.get_contents()['channels'])
        print('# %s' % st.get_contents()['channels'])
        print('# %d channels found' % len(st.get_contents()['channels']))
        curchannel = 0
        for net in st:
          results[node][y][net.code] = {}
          for sta in net:
            results[node][y][net.code][sta.code] = {}
            for cha in sta:
              results[node][y][net.code][sta.code][cha.code] = {}
              curchannel += 1
              if net.code in nets2exclude:
                print('%d/%d; Network %s is blacklisted'
                      % (curchannel, totchannels, net.code))
                continue
              # Keep track of the amount of time per request
              reqstart = time.time()
              data = Stream()
              # Days should be restricted to the days in which the stream is open
              realstart = max(t0, cha.start_date)
              realend = min(t1, cha.end_date) if cha.end_date is not None else t1
              totaldays = int((realend - realstart) / (60 * 60 * 24))
              # We have less days in the epoch than samples to select
              if totaldays <= args.days:
                print('%d/%d; Skipped because of a short epoch; %d %s %s %s'
                      % (curchannel, totchannels, y, net.code, sta.code, cha.code))
                continue
              days = random.sample(range(1, totaldays+1), args.days)
              hours = random.sample(range(0, 24),
                                    args.hours) # create random set of hours and days for download test
              hours_with_data = 0
              days_with_metrics = 0
              # Get the inventory for the whole year to test
              metadataProblem = False
              try:
                inventory = rsClient.get_stations(network=net.code,
                                                  station=sta.code,
                                                  channel=cha.code,
                                                  starttime=realstart,
                                                  endtime=realend,
                                                  level='response')
              except Exception:
                # If there are problems retrieving metadata signal it in metadataProblem
                metadataProblem = True
              # for day in tqdm(days) : # loop through all the random days
              for day in days: # loop through all the random days
                # Check WFCatalog for that day
                try:
                  auxstart = realstart + day * (60*60*24)
                  auxend = realstart + (day+1) * (60*60*24)
                  _ = wfcatalog(net.code, sta.code, cha.code, auxstart, auxend)
                  days_with_metrics += 1
                except Exception as e:
                  print(e)
                for hour in hours: # loop through all the random hours (same for each day)
                  start = realstart + day * (60*60*24) + hour * (60*60)
                  end = start + (args.minutes * 60)
                  try:
                    # get the data
                    data_temp = rsClient.get_waveforms(network=net.code,
                                                       station=sta.code,
                                                       location='*',
                                                       channel=cha.code,
                                                       starttime=start,
                                                       endtime=end)
                    data_temp.trim(starttime=start, endtime=end)
                    # Test metadata only in the case that we think it is OK
                    if not metadataProblem:
                      for tr in data_temp:
                        tr.remove_response(inventory=inventory)
                        if tr.data[0] != tr.data[0]:
                          metadataProblem = True
                          print('Error with metadata!')
                          break
                    data += data_temp
                    hours_with_data += 1
                  except Exception as e:
                    print(y, cha, node, net, sta, day, hour, e)
                    print('----------------------------')
              full_time = args.days * args.hours * args.minutes * 60
              if hours_with_data > 0: # check how much data was downloaded
                locs = []
                for tr in data:
                  locs.append(tr.stats.location)
                locs = list(set(locs))
                if len(locs) > 1:
                  completeness_by_loc = [[], [], []]
                  for loc in locs:
                    data_temp = data.copy().select(location=loc)
                    total_time_covered = 0
                    for tr in data_temp:
                      time_covered = min(tr.stats.endtime - tr.stats.starttime,
                                         args.minutes*60.0)
                      total_time_covered += time_covered
                    percentage_covered = total_time_covered / full_time
                    completeness_by_loc[0].append(loc)
                    completeness_by_loc[1].append(total_time_covered)
                    completeness_by_loc[2].append(percentage_covered)
                  percentage_covered = max(completeness_by_loc[2])
                  total_time_covered = max(completeness_by_loc[1])
                else:
                  total_time_covered = 0
                  for tr in data:
                    # Maximum of time is what we requested. If the DC sends
                    # more we consider only the requested time
                    time_covered = min(tr.stats.endtime - tr.stats.starttime,
                                       args.minutes * 60.0)
                    total_time_covered += time_covered
                  percentage_covered = total_time_covered / full_time
              else:
                total_time_covered = 0.0
                percentage_covered = 0.0
              minutes = (time.time()-reqstart)/60.0
              print('%d/%d; %8.2f min; %d %s %s %s; perc received %3.1f; perc w/metrics %3.1f; %s' %
                    (curchannel, totchannels, minutes, y, net.code, sta.code, cha.code,
                     percentage_covered * 100.0, days_with_metrics*100.0/args.days,
                     'ERROR' if metadataProblem else 'OK'))
              results[node][y][net.code][sta.code][cha.code] = {'percentage': percentage_covered,
                                                                'days_with_metrics': days_with_metrics,
                                                                'metadata_problem': metadataProblem}
      except Exception as e:
       print('No Stations available at node: '+node)
       print(e)
  with open(args.output_filename,'w') as output:
    json.dump(results, output)

if __name__ == '__main__':
  main()
