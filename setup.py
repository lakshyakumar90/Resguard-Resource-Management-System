from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="resguard",
    version="1.0.0",
    author="Lakshya kumar",
    author_email="lakshyakumar5023@gmail.com",
    description="Dynamic Resource Management System using Banker's Algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lakshyakumar90/Resguard-Resource-Management-System",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "resguard=main:main",
        ],
    },
)
