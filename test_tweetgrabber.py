import pytest
import tweetgrabber

def test_toList():
    list1 = []
    list2 = []
    tweetgrabber.toList(list1, list2)
    assert list1 == list2

