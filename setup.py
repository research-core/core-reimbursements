import os
from setuptools import find_packages, setup


setup(
    name='core-reimbursements',
    version=1.0,
    description='Core purchases reimbursements',
    author=[
        'Hugo Cachitas',
        'Ricardo Ribeiro',
    ],
    author_email=[
        'hugo.cachitas@research.fchampalimaud.org',
        'ricardo.ribeiro@research.fchampalimaud.org',
    ],
    packages=find_packages(),
    include_package_data=True,
    requirements=[
        'localflavor'
    ]
)
