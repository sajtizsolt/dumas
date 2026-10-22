from pathlib import Path

import pytest

from dumas.argumentparser import ArgumentParser


def test_argument_parser_valid_config(tmp_path: Path) -> None:
    dummy_config = tmp_path / "config.json"
    dummy_config.write_text("{}", encoding="utf-8")

    args = ArgumentParser.verify_arguments([str(dummy_config), "--logging-level", "10"])
    assert args.configuration_path == str(dummy_config)
    assert args.logging_level == 10
    assert ArgumentParser.configuration_path == str(dummy_config)
    assert ArgumentParser.logging_level == 10


def test_argument_parser_missing_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DUMAS_CONFIG", raising=False)
    with pytest.raises(SystemExit):
        ArgumentParser.parse_arguments([])


def test_argument_parser_nonexistent_file() -> None:
    with pytest.raises(SystemExit):
        ArgumentParser.parse_arguments(["/path/does/not/exist.json"])


def test_argument_parser_invalid_logging_level(tmp_path: Path) -> None:
    dummy_config = tmp_path / "config.json"
    dummy_config.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit):
        ArgumentParser.parse_arguments([str(dummy_config), "--logging-level", "99"])


def test_argument_parser_env_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_config = tmp_path / "config.json"
    dummy_config.write_text("{}", encoding="utf-8")

    monkeypatch.setenv("DUMAS_CONFIG", str(dummy_config))
    args = ArgumentParser.verify_arguments([])
    assert args.configuration_path == str(dummy_config)
