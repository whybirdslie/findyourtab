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
    },
    author="whybirdslie",
    author_email="whybirdslie@gmail.com",
    description="Universal Browser Tab Manager for Windows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/whybirdslie/findyourtab",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
    license="MIT",
) 