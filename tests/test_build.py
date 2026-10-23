from zipfile import ZipFile

from scripts.build import RUNTIME, build


def test_archive_is_clean_and_reproducible(tmp_path):
    first = build(tmp_path / "one.ankiaddon")
    second = build(tmp_path / "two.ankiaddon")
    assert first.read_bytes() == second.read_bytes()
    with ZipFile(first) as archive:
        assert set(archive.namelist()) == RUNTIME | {"LICENSE"}
        assert archive.testzip() is None
