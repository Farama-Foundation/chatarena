from setuptools import setup, find_packages

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
gradio_requirements = ["gradio==3.20.0"]
pettingzoo_requirements = ["pettingzoo==1.23.0", "chess==1.9.4"]


all_backends = anthropic_requirements + cohere_requirements + hf_requirements + bard_requirements
all_envs = pettingzoo_requirements
all_requirements = anthropic_requirements + cohere_requirements + hf_requirements + \
                   gradio_requirements + pettingzoo_requirements + bard_requirements

setup(
    name="chatarena",
    version="0.1.10.2",
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
        "pettingzoo": pettingzoo_requirements,
        "gradio": gradio_requirements,
        "all_backends": all_backends,
        "all": all_requirements,
    },
)
