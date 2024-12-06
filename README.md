# eida-data-monitoring
*Spot checks for the retrievability of seismic waveform data from the EIDA data centers.*

This is a collection of python scripts to facilitate spot checking the data hosted by the EIDA data centers for retrievability by an end user.
It is built on the [obspy](https://github.com/obspy/obspy) library, and plotting is done with [cartopy](https://github.com/SciTools/cartopy).
This project was supported by the "2022 ORFEUS Software Development Grants".

### Requirements

- [python 3.9](https://www.python.org/)
- [obspy](https://github.com/obspy/obspy)
- [cartopy](https://github.com/SciTools/cartopy)

The scripts provided here build on each other to produce station map of data retrievability like this one:

![retrievability map](https://github.com/doukutsu/eida-data-monitoring/blob/main/retrievability_europe.png "retrievability in europe")

## 1. check_retrievability.py

First, the testing script has to be run to produce the output *results.json*. This will attempt to download small chunks of data and to correct the station response, using the obspy client. It can be configured with command line arguments:

- '-s', '--start', type=int, Year to start the test (default=last year).
- '-e', '--end', type=int, Year to end the test (default=last year).
- '--days',  type=int, How many days to randomly pick from the year (default=5).
- '--hours',  type=int, How many hours to randomly pick from each day (default=2).
- '--minutes', type=int, Length of each individual download request in minutes (default=10).
- '-t', '--timeout', type=int, Number of seconds to be used as a timeout for the HTTP calls (default=30).
- '-x', '--exclude', type=str, List of comma-separated networks to be excluded from this test (e.g. XX,YY,ZZ).
- '-a', '--authentication', type=str, File containing the token to use during the authentication process (default=\~/.eidatoken).
- '--start_month', type=int, Month to start the test (default=1).
- '--end_month', type=int, Month to end the test (default=12).
- '--start_day', type=int, Day of the month to start the test (default=1).
- '--end_day', type=int, Day of the month to end the test (default=31).
- '-r', '--eida_routing', type=bool, Switch to choose between eida routing and individual node clients (default=True).
- '-o', '--output_filename', type=str, Filename to write the results to (default="results.json").

## 2. make_coordinate_list.py

A list of stations with their respective coordinates needs to be provided for the map plotting. This list should be as complete as possible, so that stations which were unreachable during the test still show up in this map. This list will be generated by the *make_coordinate_list.py* script by querying the information from the obspy client. It can be configured in the following way:
- '-s', '--start', type=int, Year to start the test (default=last year).
- '-e', '--end', type=int, Year to end the test (default=last year).
- '-r', '--eida_routing', type=bool, Switch to choose between eida routing and individual node clients (default=True).
- '-a', '--authentication', type=str, File containing the token to use during the authentication process (default=\~/.eidatoken).
- '-t', '--timeout', type=int, Number of seconds to be used as a timeout for the HTTP calls (default=30).

It might be necessary to run the *make_coordinate_list.py* script at a different time than the *check_retrievability.py* script to ensure good coverage. Alternatively, a list of station coordinates can be provided from a different source, in JSON format adhering the following structure:\
**{"network_code":{"station_code": {"latitude": *latitude_in_degs*, "longitude": *longitude_in_deg*, "elevation": *elevation_in_m* }}}**

By default, the plotting script will expect the coordinate file to by named "*coordinates.json*".

## 3. plot_result.py

The results of the tests are plotted into a map with this script. Any JSON-file residing in the project folder containing the string "results" in its name will be loaded, and the mean value for each station will be calculated from them all. By default, a detail map of europe is produced, as well as a global overview map. The background is made up of satellite images provided by Google, via cartopy.
The script accepts the following input arguments:
- '-c', '--coords_filename', type=str, Name of the file containing the station coordinates information (default="coordinates.json").
- '-g', '--global_overview_map', type=bool, Switch for plotting the global overview map (default=True).
- '-o', '--output_filename', type=str, Filename to write the results to (default="retrievability").
- '-r', '--results_directory', type=str, Directory with the result files (default=".").
- '-t', '--type', default='ret', type=str, Type of the result to plot (actual retrievability (ret) or waveform catalogue info (wfc)) (default=ret).
