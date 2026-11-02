from setuptools import setup, find_packages

setup(
    name="dark-youtube-publisher",
    version="1.0.0",
    description="DARK STUDIO AAA — YouTube Data API v3 Integration",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "google-api-python-client>=2.108.0",
        "google-auth>=2.23.4",
        "google-auth-oauthlib>=1.1.0",
        "google-auth-httplib2>=0.1.1",
        "requests>=2.31.0",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "dark-youtube=dark_youtube_publisher.cli.dark_youtube_cli:main",
        ],
    },
)
