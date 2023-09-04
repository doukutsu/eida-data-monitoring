# eida-data-monitoring
*Spot checks for the retrievability of seismic waveform data from the EIDA data centers.*

This is a collection of python scripts to facilitate spot checking the data hosted by the EIDA data centers for retrievability by an end user.
It is built on the [obspy](https://github.com/obspy/obspy) library, and plotting is done with [cartopy](https://github.com/SciTools/cartopy).

The scripts provided here build on each other to produce station map of data retrievability like this one:

![retrievability map](https://github.com/doukutsu/eida-data-monitoring/blob/main/retrievability_europe.png "retrievability in europe")

## 1. check_retrievability.py

First, run the testing script to produce the output *results.json*. This will attempt to download small chunks of data and to correct the station response. It can be configured with command line arguments:

'-s', '--start', default=sy, type=int, Year to start the test (default=last year).
'-e', '--end', default=ey, type=int, Year to end the test (default=last year).
'--days', default=5, type=int, 'How many days to randomly pick from the year (default=5).')
'--hours', default=2, type=int, 'How many hours to randomly pick from each day (default=2).')
'--minutes', default=10, type=int, 'Length of each individual download request in minutes (default=10).')
'-t', '--timeout', default=30, type=int, 'Number of seconds to be used as a timeout for the HTTP calls (default=30).')
'-x', '--exclude', default=None, 'List of comma-separated networks to be excluded from this test (e.g. XX,YY,ZZ).')
'-a', '--authentication', default=('~/.eidatoken'), 'File containing the token to use during the authentication process (default=~/.eidatoken).
'--start_month', default=1, type=int, 'Month to start the test (default=1).
'--end_month', default=12, type=int, 'Month to end the test (default=12).
'--start_day', default=1, type=int, 'Day of the month to start the test (default=1).
'--end_day', default=31, type=int, 'Day of the month to end the test (default=31).
'-r', '--eida_routing', default=True, type=bool, 'Switch to choose between eida routing and individual node clients (default=True).
'-o', '--output_filename', default="results.json", type=str, 'Filename to write the results to (default="results.json").

