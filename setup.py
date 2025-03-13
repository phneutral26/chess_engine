from setuptools import setup, find_packages

setup(
    name="chess_engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "python-chess>=1.9.0",
    ],
    entry_points={
        "console_scripts": [
            "chess-engine=chess_engine.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python-based chess engine",
    keywords="chess, engine, game",
    python_requires=">=3.7",
) 