# eida-data-monitoring
Spot checks for the retrievability of seismic waveform data from the EIDA data centers.

This is a collection of python scripts to facilitate spot checking the data hosted by the EIDA data centers for retrievability by an end user.
It is built on the [obspy](https://github.com/obspy/obspy) library, and plotting is done with [cartopy](https://github.com/SciTools/cartopy).

The scripts provided here build on each other to produce station map of data retrievability like this one:

![retrievability map](https://github.com/doukutsu/eida-data-monitoring/blob/main/retrievability_europe.png "retrievability in europe")
