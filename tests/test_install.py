import sys

import pytest

import install


@pytest.fixture()
def method():
    return "caveman"


def run(args):
    sys_argv = ["install.py", "--method", args[0], "--into", str(args[1])]
    if args[2]:
        sys_argv.append("--force")
    if args[3]:
        sys_argv.append("--dry-run")
    real_argv = sys.argv
    sys.argv = sys_argv
    try:
        return install.main()
    finally:
        sys.argv = real_argv


def test_fresh_install_isolated_from_other_skills(tmp_path, method):
    other = tmp_path / "skills" / "unrelated"
    other.mkdir(parents=True)
    other_skill = other / "SKILL.md"
    other_skill.write_text("not ours")

    dest = (tmp_path / "skills" / method).resolve()
    assert run([method, tmp_path / "skills", False, False]) == 0
    assert (dest / "SKILL.md").is_file()
    assert (dest / install.MANIFEST).is_file()
    assert other_skill.read_text() == "not ours"


def test_clean_reinstall_is_upgrade_without_backup(tmp_path, method):
    assert run([method, tmp_path / "skills", False, False]) == 0
    dest = (tmp_path / "skills" / method).resolve()

    assert run([method, tmp_path / "skills", False, False]) == 0
    backups = list((tmp_path / "skills").glob(f"{method}.backup-*"))
    assert backups == []


def test_local_modification_blocks_reinstall_without_force(tmp_path, method):
    assert run([method, tmp_path / "skills", False, False]) == 0
    dest = (tmp_path / "skills" / method).resolve()
    (dest / "SKILL.md").write_text("locally edited")

    assert run([method, tmp_path / "skills", False, False]) == 1
    assert (dest / "SKILL.md").read_text() == "locally edited"
    assert list((tmp_path / "skills").glob(f"{method}.backup-*")) == []


def test_local_modification_backed_up_and_overwritten_with_force(tmp_path, method):
    assert run([method, tmp_path / "skills", False, False]) == 0
    dest = (tmp_path / "skills" / method).resolve()
    (dest / "SKILL.md").write_text("locally edited")

    assert run([method, tmp_path / "skills", True, False]) == 0
    backups = list((tmp_path / "skills").glob(f"{method}.backup-*"))
    assert len(backups) == 1
    assert (backups[0] / "SKILL.md").read_text() == "locally edited"
    assert (dest / "SKILL.md").read_text() != "locally edited"


def test_foreign_dir_left_alone_unless_forced(tmp_path, method):
    dest = (tmp_path / "skills" / method).resolve()
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("someone else's skill")

    assert run([method, tmp_path / "skills", False, False]) == 1
    assert (dest / "SKILL.md").read_text() == "someone else's skill"

    assert run([method, tmp_path / "skills", True, False]) == 0
    assert (dest / "SKILL.md").read_text() != "someone else's skill"
    assert list((tmp_path / "skills").glob(f"{method}.backup-*"))


def test_dry_run_changes_nothing(tmp_path, method):
    assert run([method, tmp_path / "skills", False, True]) == 0
    assert not (tmp_path / "skills").exists()


def test_manifest_records_files_and_commit(tmp_path, method):
    assert run([method, tmp_path / "skills", False, False]) == 0
    manifest = install.read_manifest((tmp_path / "skills" / method).resolve() / install.MANIFEST)
    assert manifest["method"] == method
    assert manifest["source_commit"]
    assert "SKILL.md" in manifest["files"]