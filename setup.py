
import os
import sys

from setuptools import setup, find_packages

assert sys.version_info >= (2, 7), "Python 2.7+ required."

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir + os.sep + 'src')

from selena import VERSION
release = ".".join(str(num) for num in VERSION)


setup(
    name='selena',
    version=release,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    description="Simple CURL based monitoring system.",
    author='Grupa Allegro Sp. z o.o. and Contributors',
    url='http://github.com/allegro/selena',
    author_email='it-ralph-dev@allegro.pl',
    license='Apache Software License v2.0',
    install_requires=[
        "django==1.5.1",
        "lck.django==0.8.9",
        "MySQL-python==1.2.3",
        "South==0.7.6",
        "pycurl==7.18.1",
        "django-tastypie==0.9.14",
        "rq==0.3.7",
        "django-rq==0.4.6",
        "selena-agent==1.0.0",
    ],
    zip_safe=False,
)
