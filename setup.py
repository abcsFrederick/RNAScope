from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'girder>=3',
    'girder-worker[girder]',
    'large-image[pil,tiff,openslide]',
    # 'large_image_source_tiff',
    # 'large_image_source_openslide',
    # 'large-image[sources];sys.platform=="linux"',
    # 'large-image[sources];sys.platform=="linux2"',
    # 'large-image[pil];sys.platform!="linux" and sys.platform!="linux2"',
    'girder-large-image',
    'girder-large-image-annotation',
    'girder-slicer-cli-web[girder]',
    'histomicsui'
]

setup(
    author='Tianyi Miao',
    author_email='tymiao1220@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    description='Girder v3 adaptation of RNAScope',
    install_requires=requirements,
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='girder-plugin, rnascope_girder3',
    name='girder-rnascope',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/abcsFrederick/RNAScope',
    version='0.1.0',
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'rnascope = girder_rnascope:RNAScopePlugin'
        ]
    }
)
