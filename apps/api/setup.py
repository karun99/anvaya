from setuptools import setup, find_packages

setup(
    name="anvaya-api",
    version="1.0.0",
    packages=find_packages(),
    package_dir={"": "apps/api"},
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg",
        "python-jose",
        "passlib",
        "python-multipart",
        "pydantic",
        "httpx",
        "python-dotenv",
        "pgvector",
    ],
)
