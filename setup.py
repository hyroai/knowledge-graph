import setuptools

with open("README.md", "r") as fh:
    _LONG_DESCRIPTION = fh.read()


setuptools.setup(
    name="knowledge-graph",
    version="0.0.1",
    python_requires=">=3.9.5",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        "dataclasses_json==0.5.5",
        "cloud-utils @ https://github.com/hyroai/cloud-utils/tarball/b1fd9640ead5daac633ae372296a7efe2fcf2fed",
        "immutables",
        "pytest",
        "phonenumbers",
    ],
)
