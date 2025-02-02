import setuptools

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="goodreads-scraper-gauravshetty48", # Replace with your own username
    version="0.0.1",
    author="Gaurav Shetty",
    author_email="gauravshetty4@gmail.com",
    description="A package to scrape GoodReads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gauravshetty48/GoodReadsScraper",
    packages=setuptools.find_packages(),
    install_requires=[
        'beautifulsoup4==4.7.1',
        'langdetect==1.0.7',
        'selenium==3.141.0',
        'lxml==4.3.1'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)