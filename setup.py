import os
from setuptools import setup, find_packages

setup(
    name='use',
    version='0.1',
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    url='https://github.com/furious-luke/use',
    description='A Python based build system taking some of the great ideas from SCons, the well established rule based methods of make, and adding a powerful configuration system.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    license='BSD',

    packages=find_packages(),
    scripts=['use/scripts/use'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
)
