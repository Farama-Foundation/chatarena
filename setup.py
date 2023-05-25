from setuptools import setup, find_packages

_deps = [
    "openai==0.27.2",
    "anthropic==0.2.8",
    "cohere==4.3.1",
    "transformers>=4.27.4",
    "tenacity==8.2.2",
    "gradio==3.20.0",
    "rich==13.3.3",
    "prompt_toolkit==3.0.38",
    "pettingzoo==1.23.0",
    "chess==1.9.4",
    "bardapi==0.1.11",
]

with open("README.md", "r") as f:
    long_description = f.read()

requirements = _deps

setup(
    name="chatarena",
    version="0.1.10",
    author="Yuxiang Wu",
    author_email="yuxiang.cs@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chatarena/chatarena",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)
