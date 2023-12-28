from setuptools import setup, find_packages

setup(
    name='christmas_api',
    version='0.1.0',
    package=find_packages(),
    install_requires=['requests',
        'pydantic',
	'typing',],
    )
