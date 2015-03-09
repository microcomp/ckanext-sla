from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-sla',
    version=version,
    description="SLA management",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Dominik Kapisinsky',
    author_email='kapisinsky@microcomp.sk',
    url='http://github.com/microcomp',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.sla'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        sla = ckanext.sla.plugin:SlaPlugin
        [paste.paster_command]
        sla-cmd = ckanext.sla.sla_cmd:SlaCmd
    ''',
)
