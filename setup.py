from setuptools import setup, find_packages

readme = ""
with open("README.md") as f:
    readme = f.read()

setup(
    name="pyvod-chat",
    version="0.2.1",
    description="A simple library and/or CLI tool for downloading a past Twitch.tv broadcast's (VOD) chat comments.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/sixP-NaraKa/pyvod-chat",
    license="MIT",
    author="sixP-NaraKa",
    author_email="sixpaths-naraka@protonmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "python-dotenv>=0.10.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ]
)
