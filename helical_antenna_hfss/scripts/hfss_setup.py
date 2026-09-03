"""HFSS adaptive solution, frequency sweep, and far-field setup.

Convergence numbers are configuration, not results. MESH_CONVERGENCE.md must
not claim convergence unless HFSS actually reports it.
"""

from __future__ import annotations

from common import (
    ASSUMPTIONS,
    DESIGN_NAME,
    FAR_FIELD_NAME,
    PROJECT_NAME,
    SETUP_NAME,
    SOURCE,
    SWEEP_NAME,
    repo_root,
    sweep_includes_operating_frequency,
    write_json,
)


def solver_configuration() -> dict:
    sweep = sweep_includes_operating_frequency()
    return {
        "project_name": PROJECT_NAME,
        "design_name": DESIGN_NAME,
        "solution_type": ASSUMPTIONS["solution_type"],
        "model_units": ASSUMPTIONS["model_units"],
        "adaptive_setup": {
            "name": SETUP_NAME,
            "frequency_GHz": SOURCE["operating_frequency_GHz"],
            "frequency_provenance": "SOURCE_SPECIFICATION",
            "maximum_passes": ASSUMPTIONS["max_passes"],
            "minimum_passes": ASSUMPTIONS["min_passes"],
            "minimum_converged_passes": ASSUMPTIONS["min_converged_passes"],
            "max_delta_s": ASSUMPTIONS["max_delta_s"],
            "percent_refinement": ASSUMPTIONS["percent_refinement"],
            "basis_order": ASSUMPTIONS["basis_order"],
            "setup_provenance": "ENGINEERING_ASSUMPTION",
        },
        "frequency_sweep": {
            "name": SWEEP_NAME,
            "type": ASSUMPTIONS["sweep_type"],
            "start_GHz": ASSUMPTIONS["sweep_start_GHz"],
            "stop_GHz": ASSUMPTIONS["sweep_stop_GHz"],
            "step_MHz": ASSUMPTIONS["sweep_step_MHz"],
            "save_fields": False,
            "save_rad_fields": True,
            **sweep,
        },
        "far_field": {
            "name": FAR_FIELD_NAME,
            "theta_deg": [ASSUMPTIONS["theta_start_deg"], ASSUMPTIONS["theta_stop_deg"], ASSUMPTIONS["theta_step_deg"]],
            "phi_deg": [ASSUMPTIONS["phi_start_deg"], ASSUMPTIONS["phi_stop_deg"], ASSUMPTIONS["phi_step_deg"]],
        },
        "mesh": {
            "method": "HFSS adaptive lambda refinement",
            "initial_mesh": "HFSS default at solution frequency",
            "convergence_reported": False,
            "convergence_note": "NOT SIMULATED — do not treat MaxDeltaS configuration as a measured residual.",
        },
    }


def apply_setup_to_hfss(hfss) -> None:
    cfg = solver_configuration()
    setup = hfss.create_setup(SETUP_NAME)
    setup.props["Frequency"] = f"{SOURCE['operating_frequency_GHz']}GHz"
    setup.props["MaximumPasses"] = ASSUMPTIONS["max_passes"]
    setup.props["MinimumPasses"] = ASSUMPTIONS["min_passes"]
    setup.props["MinimumConvergedPasses"] = ASSUMPTIONS["min_converged_passes"]
    setup.props["MaxDeltaS"] = ASSUMPTIONS["max_delta_s"]
    setup.props["PercentRefinement"] = ASSUMPTIONS["percent_refinement"]
    try:
        setup.update()
    except Exception:
        pass
    npts = cfg["frequency_sweep"]["nominal_point_count"]
    hfss.create_linear_count_sweep(
        setup=SETUP_NAME,
        unit="GHz",
        start_frequency=ASSUMPTIONS["sweep_start_GHz"],
        stop_frequency=ASSUMPTIONS["sweep_stop_GHz"],
        num_of_freq_points=int(npts),
        name=SWEEP_NAME,
        sweep_type="Interpolating",
        save_fields=False,
        save_rad_fields=True,
    )
    hfss.insert_infinite_sphere(
        name=FAR_FIELD_NAME,
        theta_range=(
            ASSUMPTIONS["theta_start_deg"],
            ASSUMPTIONS["theta_stop_deg"],
            ASSUMPTIONS["theta_step_deg"],
        ),
        phi_range=(
            ASSUMPTIONS["phi_start_deg"],
            ASSUMPTIONS["phi_stop_deg"],
            ASSUMPTIONS["phi_step_deg"],
        ),
    )


def generate() -> dict:
    data = solver_configuration()
    write_json(repo_root() / "hfss" / "setup" / "solver_configuration.json", data)
    return data


if __name__ == "__main__":
    print(generate()["adaptive_setup"])
