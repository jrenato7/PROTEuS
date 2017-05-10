from setuptools import setup

setup(
    name='proteus',
    packages=['proteus'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
# virtualenv --system-site-packages proteusenv
