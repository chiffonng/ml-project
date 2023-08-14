from setuptools import setup, find_packages
from typing import List

HYPEN_E_DOT = "-e ."

def get_requirements(filename:str) -> List[str]:
    """Return the list of requirements from a file

    Args:
        filename (str): The path to the requirements file

    Returns:
        List[str]: The list of requirements
    """
    with open(filename) as f:
        requirements = f.read().splitlines()
        
        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
            
    return requirements

setup(
    name="mlproject",
    version="0.0.1",
    author="Chiffon Nguyen",
    author_email="chiffonng136@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt")
)