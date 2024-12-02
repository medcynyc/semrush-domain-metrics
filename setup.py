from setuptools import setup, find_packages

setup(
    name="semrush-domain-metrics",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.25.2",
        "pydantic>=2.5.2",
        "pydantic-settings>=2.0.3",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "python-dotenv>=1.0.0"
    ]
)
