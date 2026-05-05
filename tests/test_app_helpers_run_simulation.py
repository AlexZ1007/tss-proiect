import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import app_helpers


class TestRunSimulation:
    """Decision/branch-oriented tests for run_simulation."""

    def test_run_simulation_returns_false_when_not_user_triggered_and_active_exists(self, monkeypatch):
        # Simulate an existing active run in session state.
        session = {
            "active_simulation": {"existing": True},
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: session)

        called = {"value": False}

        def fake_build_simulation(venit: float, an: int):
            # If this runs, the guarded branch failed.
            called["value"] = True
            return {"venit_brut": venit, "anul_fiscal": an}

        monkeypatch.setattr(app_helpers, "build_simulation", fake_build_simulation)

        result = app_helpers.run_simulation(120000, 2024, False)

        assert result is False
        assert called["value"] is False
        assert session["active_simulation"] == {"existing": True}
        assert session["flash_message"] is None
        assert session["last_run_at"] is None

    def test_run_simulation_returns_true_and_updates_active_simulation(self, monkeypatch):
        # Force rerun through the user-triggered path.
        session = {
            "active_simulation": {"existing": True},
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: session)

        expected_payload = {"venit_brut": 150000.0, "anul_fiscal": 2025}
        monkeypatch.setattr(app_helpers, "build_simulation", lambda venit, an: expected_payload)

        result = app_helpers.run_simulation(150000, 2025, True)

        assert result is True
        assert session["active_simulation"] == expected_payload
        assert session["last_run_at"] is not None
        assert isinstance(session["last_run_at"], str)

    def test_run_simulation_sets_flash_message_only_when_user_triggered(self, monkeypatch):
        expected_payload = {"venit_brut": 90000.0, "anul_fiscal": 2024}

        # Branch 1: user_triggered=True should set flash message.
        first_session = {
            "active_simulation": None,
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: first_session)
        monkeypatch.setattr(app_helpers, "build_simulation", lambda venit, an: expected_payload)

        app_helpers.run_simulation(90000, 2024, True)
        assert first_session["flash_message"] == "Simulation run successfully."

        # Branch 2: user_triggered=False should not set flash message.
        second_session = {
            "active_simulation": None,
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: second_session)

        app_helpers.run_simulation(90000, 2024, False)
        assert second_session["flash_message"] is None

    def test_run_simulation_auto_runs_when_no_active_simulation_even_if_not_user_triggered(
        self, monkeypatch
    ):
        # Even without button click, first run should execute when active_simulation is missing.
        session = {
            "active_simulation": None,
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: session)

        expected_payload = {"venit_brut": 100000.0, "anul_fiscal": 2024, "auto": True}
        monkeypatch.setattr(app_helpers, "build_simulation", lambda venit, an: expected_payload)

        result = app_helpers.run_simulation(100000, 2024, False)

        assert result is True
        assert session["active_simulation"] == expected_payload
        assert session["last_run_at"] is not None
        assert session["flash_message"] is None

    def test_functional_equivalence_class_user_triggered_true_always_runs(self, monkeypatch):
        """
        Functional (ECP): when user_triggered is True, simulation should run
        regardless of previous active state.
        """
        session = {
            "active_simulation": {"old": "value"},
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: session)

        # Keep payload explicit so expected business output is easy to verify.
        expected_payload = {"venit_brut": 110000.0, "anul_fiscal": 2024, "source": "functional"}
        monkeypatch.setattr(app_helpers, "build_simulation", lambda venit, an: expected_payload)

        result = app_helpers.run_simulation(110000, 2024, True)

        assert result is True
        assert session["active_simulation"] == expected_payload
        assert session["flash_message"] == "Simulation run successfully."

    def test_functional_equivalence_class_user_not_triggered_with_active_does_not_run(self, monkeypatch):
        """
        Functional (ECP): when user_triggered is False and an active simulation exists,
        no rerun should happen.
        """
        existing = {"existing": "simulation"}
        session = {
            "active_simulation": existing,
            "last_run_at": "2026-05-05 16:00:00",
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: session)

        called = {"count": 0}

        def fake_build_simulation(venit: float, an: int):
            called["count"] += 1
            return {"venit_brut": venit, "anul_fiscal": an}

        monkeypatch.setattr(app_helpers, "build_simulation", fake_build_simulation)

        result = app_helpers.run_simulation(110000, 2024, False)

        assert result is False
        assert called["count"] == 0
        assert session["active_simulation"] == existing
        assert session["flash_message"] is None

    def test_functional_boundary_active_simulation_none_to_present_without_user_trigger(self, monkeypatch):
        """
        Functional (BVA on state boundary):
        - First call with active_simulation=None should run.
        - Second call (active now present) should not run.
        """
        session = {
            "active_simulation": None,
            "last_run_at": None,
            "flash_message": None,
        }
        monkeypatch.setattr(app_helpers, "st_session", lambda: session)

        payload = {"venit_brut": 70000.0, "anul_fiscal": 2024, "step": 1}
        monkeypatch.setattr(app_helpers, "build_simulation", lambda venit, an: payload)

        # Boundary left side: None -> should run automatically.
        first_result = app_helpers.run_simulation(70000, 2024, False)
        assert first_result is True
        assert session["active_simulation"] == payload

        # Boundary right side: already present -> should not rerun.
        second_result = app_helpers.run_simulation(70000, 2024, False)
        assert second_result is False
