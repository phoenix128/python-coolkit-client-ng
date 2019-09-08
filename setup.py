import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coolkit-client-ng-phoenix",
    version="1.0.0",
    author="Riccardo Tempesta",
    author_email="info@riccardotempesta.com",
    description="Sonoff control library in LAN mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phoenix128/python-coolkit-client-ng",
    packages=setuptools.find_packages(),
    install_requires=[
        'pycryptodome', 'zeroconf', 'aiohttp'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
