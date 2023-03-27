from setuptools import setup, find_packages

setup(
    name='ai_blush',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'beautifulsoup4',
        'spacy',
        'line-bot-sdk'
    ],
    entry_points={
        'console_scripts': [
            'ai_blush=ai_blush.__main__:main'
        ]
    }
)
