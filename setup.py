from setuptools import setup, find_packages

setup(
    name="bullexapi",
    version="0.1.0",
    description="Wrapper Python para Bullex API",
    author="L0k1",
    author_email="cassioms764@gmail.com",
    url="https://github.com/cassDS/bullexapi",
    packages=find_packages(),
    install_requires=["pylint", "requests", "websocket-client==1.8.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)