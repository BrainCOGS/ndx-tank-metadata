"""MazeExtension is a DynamicTable: one row per maze, one optional column per maze field."""

import math

import numpy as np
import pytest
from tests.helpers import make_lab_metadata
from ndx_tank_metadata import MazeExtension

# The fields that main declared as MazeExtension *attributes* while the Python class also offers
# them as *columns*. Writing any of them used to fail with
# "'<name>' already exists in mazes.datasets, cannot set in attributes."
FORMERLY_ATTRIBUTES = [
    "StartCycle", "EndCycle", "rule", "baseCycles", "trialNum", "hitHistory", "classHistory",
    "multibiasBeta", "multibiasTau", "pairNum", "wallGuide", "alpha_plus", "alpha_minus",
    "moonBeaconEnabled", "moonBeaconPos", "moonBeaconTrigger", "step_size", "lsrON",
    "moonDistHint", "forcedChoice",
]


def _mazes(*rows):
    mazes = MazeExtension(name="mazes", description="mazes")
    for row in rows:
        mazes.add_row(**row)
    return mazes


def _read_mazes(round_trip, mazes):
    return round_trip(make_lab_metadata(mazes=mazes)).mazes


def test_every_declared_column_round_trips(round_trip):
    mazes = MazeExtension(name="mazes", description="mazes")
    row = {k: "1" for k in mazes.mazes_attr}
    mazes.add_row(**row)
    back = _read_mazes(round_trip, mazes)
    assert len(back) == 1
    for name, value in row.items():
        assert back[name].data[0] == value, name


@pytest.mark.parametrize("name", FORMERLY_ATTRIBUTES)
def test_formerly_attribute_fields_write_as_columns(round_trip, name):
    back = _read_mazes(round_trip, _mazes({name: 3}))
    assert list(back[name].data[:]) == [3]


def test_maze_spec_declares_no_attributes_that_shadow_columns():
    from pynwb import get_type_map

    spec = get_type_map().namespace_catalog.get_spec("ndx-tank-metadata", "MazeExtension")
    own = {a.name for a in spec.attributes} - {"namespace", "neurodata_type", "object_id", "colnames", "description"}
    assert own.isdisjoint(MazeExtension.mazes_attr), own & set(MazeExtension.mazes_attr)


def test_single_row_mixed_types(round_trip):
    row = dict(world=1, lStart=5.0, rule="StartCycle < EndCycle Left", wallGuide=True, numTrials=10)
    back = _read_mazes(round_trip, _mazes(row))
    assert len(back) == 1
    assert back["world"].data[0] == 1
    assert back["lStart"].data[0] == 5.0
    assert back["rule"].data[0] == "StartCycle < EndCycle Left"
    assert bool(back["wallGuide"].data[0]) is True
    assert back["numTrials"].data[0] == 10
    assert back.id.data[0] == 0


def test_several_rows_and_string_columns(round_trip):
    rows = [
        dict(world=1, moonBeaconTrigger="Sa", cueProbability=0.8),
        dict(world=2, moonBeaconTrigger="Sb", cueProbability=1.0),
        dict(world=3, moonBeaconTrigger="", cueProbability=0.0),
    ]
    back = _read_mazes(round_trip, _mazes(*rows))
    assert list(back["world"].data[:]) == [1, 2, 3]
    assert list(back["moonBeaconTrigger"].data[:]) == ["Sa", "Sb", ""]
    assert list(back["cueProbability"].data[:]) == [0.8, 1.0, 0.0]


def test_zero_values_are_kept(round_trip):
    back = _read_mazes(round_trip, _mazes(dict(world=0, performance=0.0, easyBlock=False)))
    assert back["world"].data[0] == 0
    assert back["performance"].data[0] == 0.0
    assert bool(back["easyBlock"].data[0]) is False


def test_nan_and_inf_round_trip(round_trip):
    # ViRMEn uses NaN/Inf for "unset" cue parameters (README example: cueDuration=NaN, cueVisibleAt=Inf).
    back = _read_mazes(round_trip, _mazes(dict(cueDuration=math.nan, cueVisibleAt=math.inf),
                                          dict(cueDuration=1.5, cueVisibleAt=-math.inf)))
    assert math.isnan(back["cueDuration"].data[0])
    assert back["cueDuration"].data[1] == 1.5
    assert list(back["cueVisibleAt"].data[:]) == [math.inf, -math.inf]


def test_fixed_width_vector_column(round_trip):
    back = _read_mazes(round_trip, _mazes(dict(color=[0.1, 0.2, 0.3]), dict(color=[1.0, 1.0, 1.0])))
    np.testing.assert_array_equal(back["color"].data[:], [[0.1, 0.2, 0.3], [1.0, 1.0, 1.0]])


def test_only_some_columns_present(round_trip):
    back = _read_mazes(round_trip, _mazes(dict(world=1)))
    assert back.colnames == ("world",)


def test_empty_table_round_trips(round_trip):
    back = _read_mazes(round_trip, _mazes())
    assert len(back) == 0
    assert back.colnames == ()


def test_none_in_first_row_leaves_the_column_out(round_trip):
    # HDF5 has no null. For an optional predefined column, None means "column not present".
    back = _read_mazes(round_trip, _mazes(dict(world=None, lStart=5.0), dict(world=None, lStart=6.0)))
    assert back.colnames == ("lStart",)
    assert list(back["lStart"].data[:]) == [5.0, 6.0]


def test_none_for_existing_column_is_rejected():
    mazes = _mazes(dict(world=1, lStart=5.0))
    with pytest.raises(TypeError, match="None is not allowed"):
        mazes.add_row(world=None, lStart=6.0)


def test_missing_value_in_later_row_is_rejected():
    mazes = _mazes(dict(world=1, lStart=5.0))
    with pytest.raises(ValueError):
        mazes.add_row(world=2)
