import textwrap

import pytest

import validate_skill as vs

GOOD = textwrap.dedent(
    """\
    ---
    name: my-skill
    description: Does a thing and when to use it. Use when handling things.
    license: Apache-2.0
    metadata:
      author: example
      version: "1.0"
    ---

    # My Skill

    Instructions here.
    """
)


def write_skill(tmp_path, content, dirname="my-skill"):
    d = tmp_path / dirname
    d.mkdir()
    (d / "SKILL.md").write_text(textwrap.dedent(content))
    return d


def run_validate(skill_dir):
    problems = []
    vs.validate_skill(skill_dir, problems)
    return problems


def sev(problems, level):
    return [m for s, m in problems if s == level]


def test_valid_skill_has_no_errors(tmp_path):
    d = write_skill(tmp_path, GOOD)
    problems = run_validate(d)
    assert sev(problems, "error") == []
    assert sev(problems, "warning") == []


def test_missing_skill_file(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    problems = run_validate(d)
    assert "no SKILL.md" in " ".join(sev(problems, "error"))


def test_missing_name(tmp_path):
    d = write_skill(
        tmp_path,
        """\
        ---
        description: Something.
        ---
        body
        """,
    )
    problems = run_validate(d)
    assert any("'name' is required" in m for m in sev(problems, "error"))


@pytest.mark.parametrize(
    "bad_name",
    ["PDF-Processing", "-pdf", "pdf-", "pdf--processing", "a" * 65, "pdf processing"],
)
def test_invalid_name_rejected(tmp_path, bad_name):
    d = write_skill(
        tmp_path,
        f"---\nname: {bad_name}\ndescription: Something.\n---\nbody\n",
    )
    problems = run_validate(d)
    assert any(
        "'name' must be lowercase" in m or "'name' exceeds" in m
        for m in sev(problems, "error")
    )


def test_name_directory_mismatch_is_warning(tmp_path):
    d = write_skill(
        tmp_path,
        "---\nname: other-name\ndescription: Something.\n---\nbody\n",
        dirname="my-skill",
    )
    problems = run_validate(d)
    assert sev(problems, "error") == []
    assert any("does not match directory" in m for m in sev(problems, "warning"))


def test_missing_description_is_error(tmp_path):
    d = write_skill(tmp_path, "---\nname: my-skill\n---\nbody\n")
    problems = run_validate(d)
    assert any("'description' is required" in m for m in sev(problems, "error"))


def test_description_too_long(tmp_path):
    d = write_skill(tmp_path, f"---\nname: my-skill\ndescription: {'x' * 1025}\n---\nbody\n")
    problems = run_validate(d)
    assert any("'description' exceeds" in m for m in sev(problems, "error"))


def test_block_scalar_description_parses(tmp_path):
    d = write_skill(
        tmp_path,
        """\
        ---
        name: my-skill
        description: >
          Use this skill when: the user asks about things.
          Covers the thing and the other thing.
        ---
        body
        """,
    )
    problems = run_validate(d)
    assert sev(problems, "error") == []


def test_metadata_non_string_value(tmp_path):
    d = write_skill(
        tmp_path,
        "---\nname: my-skill\ndescription: Thing.\nmetadata:\n  version: 1.0\n---\nbody\n",
    )
    problems = run_validate(d)
    assert any("'metadata' values must be strings" in m for m in sev(problems, "error"))


def test_empty_body_is_warning(tmp_path):
    d = write_skill(tmp_path, "---\nname: my-skill\ndescription: Thing.\n---\n")
    problems = run_validate(d)
    assert sev(problems, "error") == []
    assert any("body is empty" in m for m in sev(problems, "warning"))


def test_malformed_frontmatter(tmp_path):
    d = write_skill(tmp_path, "no frontmatter here\n")
    problems = run_validate(d)
    assert any("missing or unparseable" in m for m in sev(problems, "error"))


def test_discover_walks_skill_dirs(tmp_path):
    write_skill(tmp_path, GOOD, dirname="one")
    write_skill(tmp_path, GOOD, dirname="two")
    (tmp_path / "README.md").write_text("not a skill")
    found = vs.discover(tmp_path)
    assert [p.name for p in found] == ["one", "two"]


def test_exit_code_strict_vs_lenient(tmp_path, capsys):
    d = write_skill(
        tmp_path,
        "---\nname: other\ndescription: Thing.\n---\nbody\n",
        dirname="my-skill",
    )
    assert vs.main([str(d)]) == 1
    capsys.readouterr()
    assert vs.main(["--lenient", str(d)]) == 0