# RAW and Processed Images

This directory contains all the RAW images and processed images from the telescope. The images are organized into subdirectories by date and object name.

## Subdirectories

* `YYYYMMDD`: Directory containing images taken on the specified date.
* `object_name`: Directory containing images of the specified object.

## Filenames

* `YYYYMMDD_HHMMSS_XXXXX.fit`: RAW image file taken at the specified date and time.
* `YYYYMMDD_HHMMSS_XXXXX_proc.fit`: Processed image file taken at the specified date and time.

## Image File Format

The images are stored in FITS format, which is a standard astronomical image file format. The images can be viewed and processed using software such as [Astropy](https://www.astropy.org/), [FITS Liberator](https://fits.gsfc.nasa.gov/fits_liberator.html), or [SAOImageDS9](https://sites.google.com/cfa.harvard.edu/saoimageds9).
