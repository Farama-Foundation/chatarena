from setuptools import setup, find_packages

_deps = [
    "cohere>=4.1.0",
    "openai>=0.27.0",
    "gradio>=3.20.0",
    "transformers>=4.0",
    "tenacity==8.2.2",
    "rich>=13.3.1",
    "prompt_toolkit>=3.0"
]

with open("README.md", "r") as f:
    long_description = f.read()

requirements = _deps

setup(
    name="chatarena",
    version="0.1.4",
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
