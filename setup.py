#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import io
import os
import sys
from glob import glob
from shutil import rmtree
try:
	# need setuptools to build wheel
    from setuptools import setup, Command
    setuptools_available = True
except ImportError:
	# works in a pinch
    from distutils.core import setup, Command
    setuptools_available = False
from distutils.spawn import spawn

if 'bdist_wheel' in sys.argv and not setuptools_available:
	print('cannot build wheel without setuptools')
	sys.exit(1)


NAME        = 'md_rbrb'
VERSION     = None
data_files  = [
	('share/doc/md_rbrb', ['README.md','README.rst','LICENSE'])
]
manifest = ''
for dontcare, files in data_files:
	for fn in files:
		manifest += "include {0}\n".format(fn)


here = os.path.abspath(os.path.dirname(__file__))

with open(here + '/MANIFEST.in', 'wb') as f:
	f.write(manifest.encode('utf-8'))

with open(here + '/md_rbrb.py', 'rb') as f:
	for ln in [x.decode('utf-8') for x in f]:
		if ln.startswith('__version__'):
			exec(ln)
			break

try:
	LONG_DESCRIPTION = ''
	LDCT = ''
	with open(here + '/README.rst', 'rb') as f:
		txt = f.read().decode('utf-8')
		#txt = txt[txt.find('`'):]
		LONG_DESCRIPTION = txt
		LDCT = 'text/x-rst'
except:
	print('\n### could not open README.rst ###\n')
	with open(here + '/README.md', 'rb') as f:
		txt = f.read().decode('utf-8')
		LONG_DESCRIPTION = txt
		LDCT = 'text/markdown'


class clean2(Command):
	description = 'Cleans the source tree'
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		os.system('{0} setup.py clean --all'.format(sys.executable))
		
		try: rmtree('./dist')
		except: pass
		
		try: rmtree('./md_rbrb.egg-info')
		except: pass
		
		nuke = []
		for (dirpath, dirnames, filenames) in os.walk('.'):
			for fn in filenames:
				if fn.endswith('.rst') \
				or fn.endswith('.pyc') \
				or fn.endswith('.pyo') \
				or fn.endswith('.pyd') \
				or fn.startswith('MANIFEST'):
					nuke.append(dirpath + '/' + fn)
		
		for fn in nuke:
			os.unlink(fn)


class rstconv(Command):
	description = 'Converts markdown to rst'
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		self.proc_dir('.')
		self.proc_dir('docs')
	
	def proc_dir(self, path):
		import m2r
		for (dirpath, dirnames, filenames) in os.walk(path):
			
			dirnames.sort()
			for fn in sorted(filenames):
				
				fn = dirpath + '/' + fn
				if not fn.endswith('.md'):
					continue
				
				rst_fn = fn[:-3] + '.rst'
				with open(fn, 'rb') as f:
					md = f.read().decode('utf-8')
				
				for kw in ['docs/help-']:
					md = md.replace('({0}'.format(kw),
						'(https://github.com/9001/r0c/blob/master/{0}'.format(kw))
				
				for kw in ['docs','clients']:
					md = md.replace('({0}/'.format(kw),
						'(https://ocv.me/static/r0c/{0}/'.format(kw))
				
				md = md.replace('* **[', '* [').replace(')** <-', ') <-')
				rst = m2r.convert(md)
				rst = rst.replace(':raw-html-m2r:`<del>', ':sub:`')
				rst = rst.replace('</del>`', '`')

				with open(rst_fn, 'wb') as f:
					f.write(rst.encode('utf-8'))


args = {
	'name'             : NAME,
	'version'          : __version__,
	'description'      : 'multilanguage Rabi-Ribi display',
	'long_description' : LONG_DESCRIPTION,
	'long_description_content_type' : LDCT,
	'author'           : 'ed',
	'author_email'     : 'md_rbrb@ocv.me',
	'url'              : 'https://github.com/9001/md_rbrb',
	'license'          : 'MIT',
	'data_files'       : data_files,
	'classifiers'      : [
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.0',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games',
		'Intended Audience :: End Users/Desktop',
		'Operating System :: Microsoft :: Windows',
		'Environment :: Console'
	],
	'cmdclass' : {
		'rstconv': rstconv,
		'clean2': clean2
	}
}


if setuptools_available:
	args.update({
		'install_requires'     : [],
		'include_package_data' : True,
		'py_modules'           : ['md_rbrb'],
		'entry_points'         : """
			[console_scripts]
			md_rbrb = md_rbrb:md_rbrb
		"""
	})
else:
	args.update({
		'packages' : ['md_rbrb'],
		'scripts'  : ['bin/md_rbrb']
	})


#import pprint
#pprint.PrettyPrinter().pprint(args)
#sys.exit(0)

setup(**args)
