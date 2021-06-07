#!/usr/bin/env python

"""Tests for `py6s_rtm_driver` package."""

import pytest
import datetime

from click.testing import CliRunner

from the_visitors import TheVisitorsAdapter
from the_visitors import cli
from rt_scenario import Scenario, Observation, Atmosphere, AtmosphereType, AtmosphericProfile, Surface, SurfaceType, Illumination, Measure, MeasureType

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'the_visitors.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

def test_basic_scenario():
    sc = Scenario(
        name="Rayleigh with AFGL US76 atmospheric profile",
        observations = [
            Observation(
                name="Test",
                atmosphere=Atmosphere(
                    name="Rayleigh", 
                    atmosphere_type=AtmosphereType.RAYLEIGH, 
                    atmospheric_profile=AtmosphericProfile.US76, 
                    concentrations={},
                    levels=None
                ),
                surface=Surface(
                    name="Black Surface",
                    surface_type=SurfaceType.LAMBERTIAN,
                    surface_parameters={
                        "reflectance": 0.0
                    }
                ),
                illumination=Illumination(
                    name="Illumination",
                    sza=30.0,
                    saa=0.0
                ),
                measures=[
                    Measure(
                        name="Sentinel-2A MSI",
                        measure_type=MeasureType.BRF_SAT,
                        vza=45.0,
                        vaa=0.0,
                        satellite="Sentinel-2A",
                        instrument="MSI",
                        bands=["7", "8"],
                    ),
                    Measure(
                        name="Sentinel-2A MSI",
                        measure_type=MeasureType.BRF_SAT,
                        vza=45.0,
                        vaa=0.0,
                        satellite="Sentinel-2A",
                        instrument="MSI",
                        bands=["7", "8"],
                    )
                ]
            )
        ]
    )

    adapter = TheVisitorsAdapter()
    adapter.validate_scenario(sc)
    adapter.compute_scenario(sc)
