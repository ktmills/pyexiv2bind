import os
from pprint import pprint
import pytest
from py3exiv2bind import Image

def test_icc_file():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.tif")
    my_image = Image(sample_file)
    icc = my_image.icc()
    pprint(icc)

def test_icc_on_jp2_file():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.jp2")
    my_image = Image(sample_file)
    with pytest.raises(AttributeError):
        icc = my_image.icc()