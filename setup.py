from setuptools import setup


setup(
    name='aao',
    version='0.0.1',
    description='Collection of spiders to scrape betting site and api',
    keywords='scraper spider betting soccer aao api',
    url='https://github.com/S1M0N38/aao',
    author='S1M0N38',
    author_email='bertolottosimone@gmail.com',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Documentation': 'https://s1m0n38.github.io/aao/',
        'Source': 'https://github.com/S1M0N38/aao',
        'Tracker': 'https://github.com/S1M0N38/aao/issues',
    },
    license='MIT',
    packages=['aao.api', 'aao.spiders'],
    install_requires=['selenium'],
    python_requires='>=3.6',
    zip_safe=False,
    )
