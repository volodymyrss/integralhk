from distutils.core import setup

setup(
        name='integral-scsystem',
        version='1.0',
        py_modules= ['scsystem'],
        package_data     = {
            "": [
                "*.txt",
                "*.md",
                "*.rst",
                "*.py"
                ]
            },
        install_requires=[
            'flask',
            'requests',
            'pylru',
        ],
        license='Creative Commons Attribution-Noncommercial-Share Alike license',
        long_description=open('README.md').read(),
        )
