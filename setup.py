from setuptools import setup, find_packages

from codecs import open
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='edictreader',
    version='0.2.0',
    description='EDICT2, JMdict and CEDICT reader and searcher in dictionary format',
    long_description=long_description,
    url='https://github.com/patarapolw/edictreader',
    author='Pacharapol Withayasakpunt',
    author_email='patarapolw@gmail.com',
    keywords='EDICT JMdict CEDICT',
    packages=find_packages(exclude=['test']),
    package_data={
        'edictreader': ['database/*']
    },
    include_package_data=True,
    python_requires='>=2.7',
    install_requires=['lxml'],
    zip_safe=True,
)
