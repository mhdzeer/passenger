from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="passenger_info",
    version="0.0.1",
    description="Extract and store passenger data from Bahrain CPR identity card",
    author="Your Name",
    author_email="your@email.com",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    long_description=long_description,
    install_requires=["frappe"],
)
