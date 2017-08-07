from setuptools import setup, find_packages

setup(name='govukurllookup',
      version='0.0.0.9000',
      description='Helper module to lookup GOV.UK content API',
      url='http://github.com/ukgovdatascience/govukurllookup',
      author='Matthew Upson',
      packages = find_packages(exclude=['tests']),
      author_email='matthew.upson@digital.cabinet-office.gov.uk',
      license='MIT',
      zip_safe=False,
      install_requires=['pandas']
      )
