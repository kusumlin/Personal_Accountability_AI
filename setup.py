from setuptools import find_packages,setup
from typing import List

E_DOT='-e .'
# create get_requirements which returns the list of requirements
def get_requirements(file_path:str)->List[str]:
    requirements=[]
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n","") for req in requirements]

        if E_DOT in requirements:
            requirements.remove(E_DOT)

    return requirements


setup(
    name = 'PERSONAL_ACCOUNTABILITY_AI',
    version='0.0.1',
    author='Kusum',
    author_email = 'kusumlin@usc.edu',
    packages=find_packages(),
    install_requires= get_requirements('requirements.txt')
    # ['pandas', 'numpy', 'seaborn']


)