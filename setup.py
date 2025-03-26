from setuptools import setup, find_packages

setup(
    name="OtakuDesuData",
    version="0.1.1",
    description="A Python library for scraping anime data from the OtakuDesu website",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Eka",
    author_email="ekazero99@gmail.com",
    url="https://github.com/BlindEka/OtakuDesuData",
    project_urls={
        "Source Code": "https://github.com/BlindEka/OtakuDesuData",
        "Issue Tracker": "https://github.com/BlindEka/OtakuDesuData/issues",
    },
    license="MIT",
    keywords=["anime", "scraping", "otakudesu", "otakudesu.cloud", "beautifulsoup", "httpx"],
    packages=find_packages(),
    install_requires=[
        "httpx",
        "beautifulsoup4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    platforms=["any"],
)
