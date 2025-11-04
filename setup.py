import re

import setuptools

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

# Inspiration: https://stackoverflow.com/a/7071358/6064135
with open('pynintendoauth/_version.py', 'r') as version_file:
    version_groups = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_groups:
        version = version_groups.group(1)
    else:
        raise RuntimeError('Unable to find version string!')

REQUIREMENTS = [
    # Add your list of production dependencies here, eg:
    'aiohttp == 3.*',
]

DEV_REQUIREMENTS = [
    'bandit >= 1.7,< 1.9',
    'black >= 23,< 26',
    'build >= 0.10,< 1.4',
    'flake8 >= 6,< 8',
    'isort >= 5,< 7',
    'mypy >= 1.5,< 1.19',
    'pytest >= 7,< 9',
    'pytest-cov >= 4,< 8',
    'twine >= 4,< 7',
]

setuptools.setup(
    name='pynintendoauth',
    version=version,
    description='A Python module to provide APIs to authenticate with Nintendo services.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/pantherale0/pynintendoauth',
    author='pantherale0',
    license='MIT',
    package_data={
        'pynintendoauth': [
            'py.typed',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    python_requires='>=3.8, <4',
)
