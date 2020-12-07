from setuptools import setup, find_packages

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

setup(
    name="afohtim_cpp_code_convention_formatter",
    version="0.0.2",
    author="Afohtim",
    author_email="afohmouth@gmail.com",
    description="uni metaprogramming lab 2",
    long_description="",
    url="",
    packages=find_packages(),
    entry_points={
        "console_scripts": ['afohtim_cpp_code_convention_formatter=afohtim_cpp_code_convention_formatter.main:main']
        },
    python_requires='>=3.6',
)