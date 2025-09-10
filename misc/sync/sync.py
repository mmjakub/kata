import hashlib
import os
import shutil
from typing import Generator


def hash_file(path: str) -> str:
    with open(path, "rb") as f:
        digest = hashlib.file_digest(f, hashlib.sha1)
    return digest.hexdigest()


def hash_tree(root: str) -> dict[str, set[str]]:
    hashes = {}
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            path = f"{dirpath}/{filename}"
            digest = hash_file(path)
            hashes.setdefault(digest, list()).append(os.path.relpath(path, root))
    return hashes


def sync_single_file(
    src_paths: list[str], dst_paths: list[str], src_root: str, dst_root: str
) -> Generator[tuple[str, ...]]:
    src_set, dst_set = set(src_paths), set(dst_paths)
    src = [p for p in src_paths if p not in dst_set]
    dst = [p for p in dst_paths if p not in src_set]
    for path in src:
        to = os.path.join(dst_root, path)
        if dst:
            yield "MOVE", os.path.join(dst_root, dst.pop()), to
        else:
            yield "COPY", os.path.join(src_root, path), to
    for path in dst:
        yield "DELETE", os.path.join(dst_root, path)


def filter_delete_ops(ops: list[tuple[str, ...]]) -> Generator[tuple[str, ...]]:
    targets = set()
    for op in ops:
        match op:
            case ("DELETE", tar):
                if tar in targets:
                    continue
            case ("MOVE" | "COPY", _, tar):
                targets.add(tar)
        yield op


def mk_sync_ops(
    src_hashes: dict[str, list[str]],
    dst_hashes: dict[str, list[str]],
    src_path: str,
    dst_path: str,
) -> list[tuple[str, ...]]:
    ops = []
    dst_rem = set(dst_hashes)

    for digest, paths in src_hashes.items():
        if digest in dst_hashes:
            ops.extend(sync_single_file(paths, dst_hashes[digest], src_path, dst_path))
            dst_rem.remove(digest)
        else:
            for path in paths:
                ops.append(
                    ("COPY", os.path.join(src_path, path), os.path.join(dst_path, path))
                )

    for digest in dst_rem:
        for path in dst_hashes[digest]:
            ops.append(("DELETE", os.path.join(dst_path, path)))

    return list(filter_delete_ops(ops))


def run_ops(ops: list[tuple[str, ...]]) -> None:
    for op in ops:
        match op:
            case ("DELETE", tar):
                os.unlink(tar)
            case ("COPY", src, dst):
                shutil.copy(src, dst)
            case ("MOVE", src, dst):
                shutil.move(src, dst)


def sync(src_path: str, dst_path: str) -> None:
    src_hashes = hash_tree(src_path)
    dst_hashes = hash_tree(dst_path)
    ops = mk_sync_ops(src_hashes, dst_hashes, src_path, dst_path)
    run_ops(ops)
