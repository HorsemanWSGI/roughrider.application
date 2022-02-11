import os
from setuptools import setup, find_packages


version = "0.2"

install_requires = [
    'horseman',
    'roughrider.routing'
]

test_requires = [
    'WebTest',
    'pytest',
]


setup(
    name='roughrider.application',
    version=version,
    author='Souheil CHELFOUH',
    author_email='trollfot@gmail.com',
    url='https://github.com/HorsemanWSGI/roughrider.application',
    download_url='http://pypi.python.org/pypi/roughrider.application',
    description='Run-of-the-mill WSGI application base with URL routing.',
    long_description=(open("README.rst").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.rst")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['roughrider',],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
)
