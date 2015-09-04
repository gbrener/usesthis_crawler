#!/usr/bin/env python


from setuptools import setup, find_packages


setup(
    name='usesthis_crawler',
    version='0.0.1',
    url='https://github.com/gbrener/usesthis_crawler.git',
    author='Greg Brener',
    author_email='gbrener@gmail.com',
    description='Crawl usesthis.com and store results in SQL database.',
    license='MIT',
    packages=find_packages(),
    entry_points=dict(
        console_scripts=['crawl-usesthis = usesthis_crawler.cli:main'],
    ),
    setup_requires=['nose >=1.0'],
    install_requires=['scrapy >=1.0.3', 'sqlalchemy >=1.0.8', 'pyasn1 >=0.1.8'],
    tests_require=['nose', 'mock', 'requests', 'coverage', 'hypothesis'],
    zip_safe=False,
)
