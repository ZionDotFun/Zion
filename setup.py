from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentipy",
    version="0.1.0",
    author="Utilify",
    author_email="hello@getutilify.com",
    description="A Python toolkit for Solana agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/niceberginc/agentipy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13.0",
    install_requires=[
        "requests==2.32.3",
        "python-dotenv==1.0.1",
        "numpy==2.2.0",
        "base58>=2.1.1",
        "aiohttp>=3.11.10",
        "pillow>=11.0.0",
        "openai>=1.58.1",
        "solana>=0.36.1",
        "solders>=0.23.0",
        "pydantic>=2.10.4",
    ],
    extras_require={
        "dev": [
            "pytest==8.3.4",
            "black==24.10.0",
            "isort>=5.10.0",
        ]
    },
    entry_points={
        'console_scripts': [
            'agentipy-cli=agentipy.cli:main',
        ],
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
