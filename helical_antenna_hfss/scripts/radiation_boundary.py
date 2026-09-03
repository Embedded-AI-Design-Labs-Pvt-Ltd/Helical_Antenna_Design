"""Compatibility alias — Agent 5 asked for radiation_boundary.py."""

from radiation_setup import apply_to_hfss, generate, radiation_definition

__all__ = ["apply_to_hfss", "generate", "radiation_definition"]


if __name__ == "__main__":
    generate()
