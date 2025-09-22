from setuptools import find_packages, setup
from typing import List

def get_reuirements() -> List:
    requirement_list: List[str] = []
    try:
        with open('requirments.txt', 'r') as file:
            lines = file.readline()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement!='-e.':
                    requirement_list.append(requirement)

        
    except FileNotFoundError:
        print("requirement.txt file not found")
    
    return requirement_list

setup(
    name="network_security",
    version="0.0.1",
    author="Tanmay Bhaise",
    author_email="tanmaybhaise143@gmail.com",
    packages=find_packages(),
    install_rquires=get_reuirements()
)