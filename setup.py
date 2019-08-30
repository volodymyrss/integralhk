from setuptools import setup

setup(
        name='integralhk',
        version='1.0',
        packages=["integralhk"],
        install_requires=[
            'flask',
            'requests',
        ],
        license='Creative Commons Attribution-Noncommercial-Share Alike license',
        long_description=open('README.md').read(),
        )
