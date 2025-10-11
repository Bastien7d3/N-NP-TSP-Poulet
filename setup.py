"""
Configuration d'installation pour le package TSP Livraison.

Ce fichier permet d'installer le package et ses dépendances de manière propre.

Usage:
    pip install -e .        # Installation en mode développement
    pip install .           # Installation standard
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tsp-livraison",
    version="1.0.0",
    author="Projet TSP Livraison",
    description="Solveur TSP avec contraintes de livraison",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tsp-livraison=main:main",
        ],
    },
    package_dir={"": "."},
    include_package_data=True,
)