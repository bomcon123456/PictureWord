from setuptools import setup

setup(
    name='ankiword',
    version='0.1.0',
    packages=['ankiword'],
    entry_points={
        'console_scripts': [
            'ankiword = ankiword.__main__:main'
        ]
    })
