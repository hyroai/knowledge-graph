import setuptools

with open("README.md", "r") as fh:
    _LONG_DESCRIPTION = fh.read()


setuptools.setup(
    name="knowledge-graph",
    version="1",
    python_requires=">=3.9.5",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Hyro AI",
    author_email="contact@hyro.ai",
    url="https://github.com/hyroai/knowledge-graph/",
    download_url="https://github.com/hyroai/knowledge-graph/archive/refs/tags/1.tar.gz",
    keywords=["tag1", "tag2"],
    classifiers=[],
    packages=setuptools.find_namespace_packages(),
    install_requires=[
        "dataclasses_json==0.5.5",
        "cloud-utils @ https://github.com/hyroai/cloud-utils/tarball/26e27a0f013aa80e0ce83c3d4d4f99f7dbfc6b99",
        "immutables",
        "pytest",
        "phonenumbers",
    ],
)
