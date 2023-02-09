from setuptools import setup


setup(
    name='cldfbench_handschuhnames',
    py_modules=['cldfbench_handschuhnames'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'handschuhnames=cldfbench_handschuhnames:Dataset',
        ]
    },
    install_requires=[
        'cldfbench[glottolog]',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
