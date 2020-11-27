
from setuptools import setup, find_packages
from pade_fmi.__version__ import __version__

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setup(name='pade-fmi',
      version=__version__,
      description='The pade-fmi adapter allows to couple FMUs, which are based on the FMI standard (https://fmi-standard.org) with PADE.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Marcos Bressan',
      author_email='bressanmarcos@alu.ufc.br',
      license='MIT',
      keywords='multiagent distributed systems',
      entry_points={
          'console_scripts': [
              'pade-fmi = pade_fmi.__main__:main'
          ]
      },
      packages=find_packages(),
      install_requires=[
          'pade',
          'pythonfmu'
      ],
      tests_require=[
          'pytest',
          'pyfmi'
      ],
      classifiers=[
              'Intended Audience :: Developers',
              'Topic :: Software Development :: Build Tools',
              'License :: OSI Approved :: MIT License',
              'Operating System :: OS Independent',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.7',
      ],)
