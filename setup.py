import subprocess

import setuptools

with open("README.md", "r") as fh:
    _LONG_DESCRIPTION = fh.read()

knowledge_graph_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in knowledge_graph_version:
    v, i, s = knowledge_graph_version.split("-")
    knowledge_graph_version = v + "+" + i + ".git." + s


setuptools.setup(
    name="knowledge-graph",
    version=knowledge_graph_version,
    python_requires=">=3.9.5",
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
        "dataclasses_json==0.5.5",
        "immutables",
        "pytest",
        "phonenumbers",
    ],
)
