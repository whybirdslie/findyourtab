from setuptools import setup, find_packages

setup(
    name="FindYourTab",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pywebview',
        'websockets',
        'keyboard'
    ],
    package_data={
        'findyourtab': ['static/*'],
    },
    entry_points={
        'console_scripts': [
            'findyourtab=findyourtab_native:main',
        ],
    }
) 