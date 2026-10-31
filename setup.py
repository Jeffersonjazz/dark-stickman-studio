"""
DARK STICKMAN STUDIO — setup.py
Permite instalar como pacote Python com: pip install -e .

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from setuptools import setup, find_packages

setup(
    name="dark-stickman-studio",
    version="1.0.0",
    description="Pipeline de produção automatizada de vídeos stickman para YouTube — DARK CREATIVE LAB",
    author="DARK STUDIO AAA",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.7.0",
        "typer>=0.12.0",
        "rich>=13.7.0",
        "Pillow>=10.3.0",
    ],
    entry_points={
        "console_scripts": [
            "dark-stickman=cli.dark_stickman:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
