import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='rechorder',  
    version='0.1',
    scripts=['rechorder'] ,
    author="Spencer Churchill",
    author_email="spencer.l.churchill@gmail.com",
    description="A microphone to sheet music converter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/splch/rechorder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
