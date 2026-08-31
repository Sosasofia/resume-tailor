from pathlib import Path

from app.profile_loader import load_profile


def test_profile_can_be_loaded() -> None:
    profile = load_profile(
        Path("data/profile.json")
    )

    assert profile.basics.name == "Victor Vigon"
    assert "Python" in profile.skills
    assert len(profile.experience) == 2
    assert len(profile.projects) == 1