# import pytest

from researchos.application.services.retriever_service import overlap_chunking


# @pytest.mark.unit
def test_overlap_chunking():
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, \
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
    nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in \
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla \
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in \
    culpa qui officia deserunt mollit anim id est laborum."

    chunk_size = 30
    overlap = 5
    chunks = overlap_chunking(
        text=text, paper_id="10205035", chunk_size=chunk_size, overlap=overlap
    )

    if len(chunks) > 1:
        assert all(len(chunk.text) == chunk_size for chunk in chunks[:-1])
        assert all(
            chunks[i].text[-overlap:] == chunks[i + 1].text[:overlap]
            for i in range(len(chunks))
            if i < len(chunks) - 1
        )
    else:
        assert chunks[0].text == text


if __name__ == "__main__":
    test_overlap_chunking()
