from setuptools import find_packages, setup

setup(
    name='O-Que-Cursar',
    packages=find_packages(),
    include_package_data=True,
    description='"O Que Cursar?" is a website develop as the Final Project for my Computer Science major',
    version='0.1',
    url='https://github.com/besenleo/O-Que-Cursar',
    author='Leonardo Henrique Besen',
    author_email='leo_besen@yahoo.com.br',
    install_requires=['psycopg2']
)