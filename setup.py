from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentipy",
    version="1.2.2",
    author="Utilify",
    author_email="hello@getutilify.com",
    description="A Python toolkit for Solana agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/niceberginc/agentipy",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests==2.32.3",
        "python-dotenv==1.0.1",
        "numpy==1.22.4,<2",
        "base58>=2.1.1",
        "aiohttp>=3.11.10",
        "pillow>=11.0.0",
        "openai>=1.58.1",
        "solana>=0.35.0",
        "solders>=0.21.0,<0.24.0",
        "pydantic>=2.10.4",
        "langchain>=0.3.12",
        "anchorpy>=0.20.1"
    ],
    extras_require={
        "dev": [
            "pytest==8.3.4",
            "black==24.10.0",
            "isort>=5.10.0",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True, 
    project_urls={
        "Bug Tracker": "https://github.com/niceberginc/agentipy/issues",
        "Documentation": "https://github.com/niceberginc/agentipy#readme",
    },
)
