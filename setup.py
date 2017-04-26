from setuptools import setup

install_requires = [
    'flask',
    'psycopg2',
]

setup_requires=[
    'pytest-runner',
]

tests_require = [
    'pytest',
]

dev_require = [
    'honcho',
]

doc_require = [
    'sphinx',
]

setup(
    name='minitwit',
    packages=['minitwit'],
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require = {
        'dev': dev_require + tests_require + doc_require,
        'test': tests_require,
        'doc': doc_require,
    },
)
