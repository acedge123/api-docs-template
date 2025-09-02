from setuptools import setup, find_packages

setup(
    name="hfc-scoring-engine",
    version="1.0.0",
    description="HFC Scoring Engine - Lead qualification and scoring API",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
)
