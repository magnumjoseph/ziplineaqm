from setuptools import setup, find_packages

setup(
		name='ziplineaqm',
		version='1.1',
		description='Aqumon Customized Zipline Environment',
		author='Joseph Chen',
		author_email='joseph.chen@magnumwm.com',
		url='https://github.com/magnumwmjoseph/ziplineaqm',
		packages=find_packages(),
		install_requires=[
			'numpy==1.16.0',
			'pandas==0.22.0',
			'pandas-datareader==0.7.0',
			'trading-calendars==1.2.0',
			'tabulate==0.8.3',
		]
)