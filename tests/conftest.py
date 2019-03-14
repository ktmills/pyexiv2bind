import os
import shutil
import tarfile

import pytest
import urllib.request


def download_images(url, destination, download_path):

        print("Downloading {}".format(url))
        urllib.request.urlretrieve(url,
                                   filename=os.path.join(download_path, "sample_images.tar.gz"))
        if not os.path.exists(os.path.join(download_path, "sample_images.tar.gz")):
            raise FileNotFoundError("sample images not download")
        print("Extracting images")
        with tarfile.open(os.path.join(download_path, "sample_images.tar.gz"), "r:gz") as archive_file:
            for item in archive_file.getmembers():
                print("Extracting {}".format(item.name))
                archive_file.extract(item, path=destination)
            pass


@pytest.fixture(scope="session")
def sample_images_readonly(tmpdir_factory):

    test_path = tmpdir_factory.mktemp("data")
    sample_images_path = os.path.join(test_path, "sample_images")
    download_path = tmpdir_factory.mktemp("downloaded_archives")
    if os.path.exists(sample_images_path):
        print("{} already exits".format(sample_images_path))

    else:
        print("Downloading sample images")
        download_images(url="https://jenkins.library.illinois.edu/userContent/sample_images.tar.gz",
                        destination=test_path,
                        download_path=download_path)

    yield sample_images_path
    shutil.rmtree(test_path)


@pytest.fixture
def sample_images(tmpdir_factory, sample_images_readonly):
    new_set = tmpdir_factory.mktemp("sample_set")
    sample_image_files = []
    for file in os.scandir(sample_images_readonly):
        sample_image_new = os.path.join(new_set, file.name)
        shutil.copyfile(file.path, sample_image_new)
        sample_image_files.append(sample_image_new)

    yield new_set
    shutil.rmtree(new_set)
