import hashlib
import os
import tempfile
from functools import partial

import sync


def test_same_files_have_same_hash():
    mk_file = tempfile.NamedTemporaryFile

    with mk_file() as f1, mk_file() as f2:
        for f in (f1, f2):
            f.write(b"foo")
            f.seek(0)
        hash1 = sync.hash_file(f1.name)
        hash2 = sync.hash_file(f2.name)

    assert hash1 != hashlib.sha1(b"").hexdigest() != hash2
    assert hash1 == hash2


def test_different_files_have_different_hash():
    mk_file = tempfile.NamedTemporaryFile

    with mk_file() as f1, mk_file() as f2:
        f1.write(b"foo")
        f1.seek(0)
        hash1 = sync.hash_file(f1.name)
        f2.write(b"bar")
        f2.seek(0)
        hash2 = sync.hash_file(f2.name)

    assert hash1 != hash2


def test_hash_tree():
    data = b"foobar"
    with (
        tempfile.TemporaryDirectory() as dname,
        tempfile.NamedTemporaryFile(dir=dname) as f,
    ):
        filename = os.path.relpath(f.name, dname)
        f.write(data)
        f.seek(0)

        hashes = sync.hash_tree(dname)

    assert hashes == {hashlib.sha1(data).hexdigest(): [filename]}


def test_hash_tree_when_there_are_duplicate_files_under_different_names():
    data = b"foobar"
    digest = hashlib.sha1(data).hexdigest()
    tmp_f = tempfile.NamedTemporaryFile
    with (
        tempfile.TemporaryDirectory() as dirname,
        tmp_f(dir=dirname) as f1,
        tmp_f(dir=dirname) as f2,
    ):
        fn = set()
        for f in (f1, f2):
            f.write(data)
            f.seek(0)
            fn.add(os.path.relpath(f.name, dirname))

        hashes = sync.hash_tree(dirname)

    assert digest in hashes
    assert set(hashes[digest]) == fn


def test_file_is_copied_if_missing():
    ops = sync.mk_sync_ops({"foo": ["c"]}, [], "a", "b")

    assert ops == [("COPY", "a/c", "b/c")]


def test_file_is_moved_if_exists_in_dst():
    ops = sync.mk_sync_ops({"foo": ["c"]}, {"foo": ["d"]}, "src_root", "dst_root")

    assert ops == [("MOVE", "dst_root/d", "dst_root/c")]


def test_extra_files_are_deleted():
    ops = sync.mk_sync_ops({"foo": ["c"]}, [], "a", "b")

    assert ops == [("COPY", "a/c", "b/c")]


def test_extra_copies_are_deleted():
    ops = sync.mk_sync_ops({"foo": ["c"]}, {"foo": ["d", "e"]}, "src_root", "dst_root")

    assert ops == [("MOVE", "dst_root/e", "dst_root/c"), ("DELETE", "dst_root/d")]


def test_dst_file_is_replaced_by_copy():
    ops = sync.mk_sync_ops({"foo": ["a"]}, {"bar": ["a"]}, "src_root", "dst_root")

    assert ops == [("COPY", "src_root/a", "dst_root/a")]


def test_dst_file_is_replaced_by_move():
    ops = sync.mk_sync_ops(
        {"foo": ["a"]}, {"foo": ["b"], "bar": ["a"]}, "src_root", "dst_root"
    )

    assert ops == [("MOVE", "dst_root/b", "dst_root/a")]


def test_sync_e2e():
    def mk_file(path, name, data):
        with open(os.path.join(path, name), "x") as f:
            f.write(data)

    with (
        tempfile.TemporaryDirectory(prefix="src_") as src,
        tempfile.TemporaryDirectory(prefix="dst_") as dst,
    ):
        mk_file(src, "copy_this", "foo")
        mk_file(src, "src_name", "bar")

        mk_file(dst, "move_this", "bar")
        mk_file(dst, "delete_this", "baz")
        mk_file(dst, "src_name", "don't delete - should be overwritten")

        sync.sync(src, dst)

        assert not os.path.exists(os.path.join(dst, "delete_this"))
        assert not os.path.exists(os.path.join(dst, "move_this"))
        with open(os.path.join(dst, "copy_this")) as f:
            assert f.read() == "foo"
        with open(os.path.join(dst, "src_name")) as f:
            assert f.read() == "bar"
