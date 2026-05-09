from setuptools import setup, find_packages

setup(
    name="presto-core",
    version="0.1.0",
    description="NFR-driven performance test generation for mission-critical systems",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Praveen Margabandhu",
    url="https://github.com/praveen-margabandhu/presto-core",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "presto=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=[
        "performance engineering",
        "load testing",
        "k6",
        "nfr",
        "slo",
        "sla",
        "performance testing",
        "ci cd",
        "mission critical",
        "presto",
    ],
)
