from setuptools import setup, find_packages

setup(
    name="pmtool-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-multipart>=0.0.5",
        "pdfplumber>=0.7.0",
        "openai>=1.0.0",
        "psycopg2-binary>=2.9.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
    ],
)
