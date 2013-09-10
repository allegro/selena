
import os
import sys

from setuptools import setup, find_packages

assert sys.version_info >= (2, 7), "Python 2.7+ required."

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src', 'selena'))

from selena.version import VERSION
release = ".".join(str(num) for num in VERSION)


setup(
    name='selena',
    version=release,
    packages=find_packages('src/selena'),
    include_package_data=True,
    package_dir={'': 'src/selena'},
    description="Simple CURL based monitoring system.",
    author='Grupa Allegro Sp. z o.o. and Contributors',
    url='http://github.com/allegro/selena',
    author_email='it-ralph-dev@allegro.pl',
    license='Apache Software License v2.0',
    install_requires=[
        "django==1.5.2",
        "lck.django==0.8.9",
        "MySQL-python==1.2.3",
        "South==0.7.6",
        "pycurl==7.18.1",
        "django-tastypie==0.9.14",
        "rq==0.3.8",
        "django-rq==0.5.1",
        "selena-agent==1.0.1",
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'selena = selena.__main__:main',
        ],
    },
)
