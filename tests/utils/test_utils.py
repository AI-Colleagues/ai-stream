from ai_stream.utils import create_id


def test_create_id():
    result = create_id()

    # Check if the length of the result is correct
    expected_length = 22  # 22 is the length of base64 encoded UUID without padding
    assert len(result) == expected_length, f"Result length is incorrect: {len(result)}"
