#!/usr/bin/env python
#
# setup.py for gnuConcept

from distutils.core import setup
from glob import glob

setup(name="gwibber",
	version="0.7",
	author="Ryan Paul",
	author_email="segphault@arstechnica.com",
  url="http://cixar.com/~segphault",
	license="GNU General Public License (GPL)",
	packages=['gwibber', 'gwibber.microblog', 'gwibber.microblog.support'],
	data_files=[
		('share/gwibber/ui/', glob("ui/*.glade")),
		('share/gwibber/ui/', glob("ui/*.png")),
		('share/gwibber/ui/themes/default', glob("ui/themes/default/*")),
		('share/gwibber/ui/themes/shine', glob("ui/themes/shine/*")),
		('share/gwibber/ui', ['ui/progress.gif']),
		('share/gwibber/ui', ['ui/gwibber.svg']),
		('share/pixmaps', ['ui/gwibber.svg']),
		('share/applications/',['gwibber.desktop'])],
	scripts=['bin/gwibber'] 
)
