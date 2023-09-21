from setuptools import setup, find_packages


# remove duplicate requirements
def remove_duplicate_requirements(requirements):
    return list(set(requirements))


with open("README.md", "r") as f:
    long_description = f.read()

base_requirements = [
    "openai>=0.27.2",
    "tenacity==8.2.2",
    "rich==13.3.3",
    "prompt_toolkit==3.0.38",

]
anthropic_requirements = ["anthropic>=0.2.8"]
cohere_requirements = ["cohere>=4.3.1"]
hf_requirements = ["transformers>=4.27.4"]
bard_requirements = ["bardapi==0.1.11"]
langchain_requirements = ["langchain>=0.0.135"]
gradio_requirements = ["gradio>=3.34.0"]
pettingzoo_requirements = ["pettingzoo[classic]>=1.23.1", "chess==1.9.4"]
umshini_requirements = ["pettingzoo>=1.23.1", "langchain>=0.0.135"]

all_backends = anthropic_requirements + cohere_requirements + hf_requirements + bard_requirements + \
               langchain_requirements
all_envs = remove_duplicate_requirements(pettingzoo_requirements + umshini_requirements)
all_requirements = all_backends + all_envs + gradio_requirements

setup(
    name="chatarena",
    version="0.1.12.10",
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
    install_requires=base_requirements,
    extras_require={
        "anthropic": anthropic_requirements,
        "cohere": cohere_requirements,
        "huggingface": hf_requirements,
        "bard": bard_requirements,
        "langchain": langchain_requirements,
        "pettingzoo": pettingzoo_requirements,
        "umshini": umshini_requirements,
        "gradio": gradio_requirements,
        "all_backends": all_backends,
        "all": all_requirements,
    },
)
