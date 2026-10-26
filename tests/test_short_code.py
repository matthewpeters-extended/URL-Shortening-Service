import pytest

from app.short_code import decode, encode


@pytest.mark.parametrize("number", [0, 1, 61, 62, 63, 12345, 999999999])
def test_roundtrip(number):
    assert decode(encode(number)) == number


def test_encode_known_values():
    assert encode(0) == "0"
    assert encode(1) == "1"
    assert encode(61) == "Z"
    assert encode(62) == "10"


def test_decode_rejects_invalid_character():
    with pytest.raises(ValueError):
        decode("not-base62!")


def test_encode_rejects_negative():
    with pytest.raises(ValueError):
        encode(-1)
