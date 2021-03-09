
from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
	name    	         			= 'movementrx',
	version     	     			= '0.2.3',
	description     	 			= 'Gait analysis using One-Dimensional Statistical Parametric Mapping',
	author           				= 'Amr ALHOSSARY',
	author_email     				= 'aalhossary@ntu.edu.sg',
	url              				= 'http://rris.ntu.edu.sg/Research/Pages/Precision-Rehabilitation-.aspx',
# 	download_url     				= 'https://github.com/0todd0000/spm1d/archive/master.zip',
	license          				= 'GPLv3',  # TODO not sure of the spelling
	# packages, package_dir, and package_data are interrelated. package_data should be relative to package_dir
	# package_data is data that is closely related to the package implementation, or text files containing documentation
	packages     	    			= find_packages(
# 									where='.', include=['*', ], exclude=[]
    								),
	package_dir 					= {'spmclient': 'spmclient',
									'spm1d': 'spm1d'}, #  {'spm1d':"src/spm1d"},  # This is different from the where parameter of fine_packages
	package_data     				= {'spmclient' : ['res/cases/*/*/*', 'res/ref*/*',],
									'spm1d' : ['examples/*', 'data/*'] },
	include_package_data 			= True,
# 	data_files						= [('movement_data', ['spmclient/res/cases/*/*/*.csv', 'res/ref*/*/*/*.csv']),
# #                   						('config', ['cfg/data.cfg'])
#                   						],
	long_description 				= long_description,
	long_description_content_type	="text/markdown",
	keywords         				= ['gait analysis', 'statistics', 'time series analysis'],
	classifiers      				= ["Programming Language :: Python :: 3",
										"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
										"Operating System :: OS Independent",],
	python_requires					='>=3.7',
	install_requires 				= ["numpy (!=1.19.4)", "scipy", "matplotlib", "pyqt5"]
)
