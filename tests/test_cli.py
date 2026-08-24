import pytest
import sys
from alloy_core.cli.main import main


def test_cli_simulate(capsys, monkeypatch):
    test_args = [
        "main.py",
        "simulate",
        "--composition", '{"Al": 0.965, "Sc": 0.007, "Zr": 0.003, "Mg": 0.025}',
        "--route", "lpbf"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    main()
    captured = capsys.readouterr()
    assert '"status": "simulated"' in captured.out
    assert '"yield_strength_mpa"' in captured.out


def test_cli_discover(capsys, monkeypatch):
    test_args = [
        "main.py",
        "discover",
        "--name", "Test Discovery",
        "--base", "Al",
        "--samples", "50",
        "--batch-size", "2"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    main()
    captured = capsys.readouterr()
    assert "=== Starting Discovery Campaign: Test Discovery ===" in captured.out
    assert "Top Pareto Candidates" in captured.out
