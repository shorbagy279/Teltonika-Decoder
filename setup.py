from setuptools import setup

# read the long description from README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="teltonika-decoder",
    version="0.1.0",
    py_modules=["decoder"],
    author="Abdulrhman Elshorbagy",
    author_email="abdulrhmanm557@gmail.com",
    description="A Python library to decode Teltonika device messages (AVL & text codecs).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shorbagy279/Teltonika-Decoder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
