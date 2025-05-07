from setuptools import setup, find_packages

setup(
    name='whistledrop',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.0.0',
        'PyCryptodome>=3.10.0',
        'requests>=2.25.0',
        'flask-cors>=3.0.9',
        'stem>=1.8.0',  # For Tor integration
    ],
    entry_points={
        'console_scripts': [
            'whistledrop=server.app:main',  # TODO: Implement main function in app.py
        ],
    },
    author='Your Name',  # TODO: Replace with your name
    author_email='your.email@example.com',  # TODO: Replace with your email
    description='A secure whistleblower platform for anonymous file uploads.',
    url='https://github.com/yourusername/whistledrop',  # TODO: Replace with your GitHub repository URL
)