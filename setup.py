from distutils.core import setup

setup(
        name='integralhk',
        version='1.0',
        py_modules= ['integalhk'],
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
        ],
        license='Creative Commons Attribution-Noncommercial-Share Alike license',
        long_description=open('README.md').read(),
        )
