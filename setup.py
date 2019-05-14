
from setuptools import setup, find_packages


__version__ = '1.3'


with open('requirements.txt') as f:
    requires = f.read().splitlines()


url = 'https://github.com/pmaigutyak/mp-shop-attrs'


setup(
    name='django-mp-shop-attrs',
    version=__version__,
    description='Django shop attributes apps',
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='{}/archive/{}.tar.gz'.format(url, __version__),
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=requires
)
