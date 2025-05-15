import setuptools

with open("README.md", "r") as fh:
    _LONG_DESCRIPTION = fh.read()


setuptools.setup(
    name="knowledge-graph",
    version="0.0.33",
    python_requires=">=3.11",
    description="A library to store data in a knowledge graph",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Hyro AI",
    author_email="contact@hyro.ai",
    url="https://github.com/hyroai/knowledge-graph/",
    keywords=["tag1", "tag2"],
    classifiers=[],
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        "dataclasses_json==0.5.7",
        "immutables",
        "pytest",
        "phonenumbers",
    ],
)
