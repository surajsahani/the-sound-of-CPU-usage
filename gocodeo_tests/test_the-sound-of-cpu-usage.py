import pytest
from unittest import mock
import psutil
from midiutil import MIDIFile
from the_sound_of_cpu_usage import clamp, genNote

@pytest.fixture
def mock_psutil_cpu_percent():
    with mock.patch('psutil.cpu_percent') as mock_cpu_percent:
        mock_cpu_percent.side_effect = lambda interval=None, percpu=False: [50, 60, 70, 80] if percpu else 75
        yield mock_cpu_percent

@pytest.fixture
def mock_midi_file():
    with mock.patch('midiutil.MIDIFile') as mock_midi:
        mock_midi_instance = mock.MagicMock()
        mock_midi.return_value = mock_midi_instance
        yield mock_midi_instance

@pytest.fixture
def setup_mocks(mock_psutil_cpu_percent, mock_midi_file):
    # Mocking the MIDIFile and psutil.cpu_percent for the tests
    pass

# happy_path - test_clamp_within_range - Test that clamp function returns the number when it is within the range.
def test_clamp_within_range():
    result = clamp(5, 0, 10)
    assert result == 5

# happy_path - test_clamp_below_range - Test that clamp function returns the smallest number when n is less than smallest.
def test_clamp_below_range():
    result = clamp(-1, 0, 10)
    assert result == 0

# happy_path - test_clamp_above_range - Test that clamp function returns the largest number when n is greater than largest.
def test_clamp_above_range():
    result = clamp(15, 0, 10)
    assert result == 10

# happy_path - test_gennote_core_0_1 - Test that genNote function adds a note with correct pitch and duration for core 0 and core 1.
def test_gennote_core_0_1(setup_mocks):
    genNote(0, 1, 0)
    mock_midi_file().addNote.assert_called_with(0, 0, 65, 1, 0.2, 100)

# happy_path - test_gennote_last_first_core - Test that genNote function adds a note with correct pitch and duration for last core and first core.
def test_gennote_last_first_core(setup_mocks):
    genNote(3, 0, 3)
    mock_midi_file().addNote.assert_called_with(3, 0, 95, 1, 0.2, 100)

# edge_case - test_clamp_equals_smallest - Test that clamp function handles when n equals smallest and returns smallest.
def test_clamp_equals_smallest():
    result = clamp(0, 0, 10)
    assert result == 0

# edge_case - test_clamp_equals_largest - Test that clamp function handles when n equals largest and returns largest.
def test_clamp_equals_largest():
    result = clamp(10, 0, 10)
    assert result == 10

# edge_case - test_gennote_pitch_core_out_of_range - Test that genNote function handles when pitch_core is out of range and defaults to 0.
def test_gennote_pitch_core_out_of_range(setup_mocks):
    genNote(5, 1, 0)
    mock_midi_file().addNote.assert_called_with(0, 0, 65, 1, 0.2, 100)

# edge_case - test_gennote_duration_core_out_of_range - Test that genNote function handles when duration_core is out of range and defaults to 0.
def test_gennote_duration_core_out_of_range(setup_mocks):
    genNote(0, 5, 0)
    mock_midi_file().addNote.assert_called_with(0, 0, 65, 1, 0.2, 100)

# edge_case - test_gennote_track_out_of_range - Test that genNote function handles when track is out of range and defaults to last track.
def test_gennote_track_out_of_range(setup_mocks):
    genNote(0, 1, 5)
    mock_midi_file().addNote.assert_called_with(3, 0, 65, 1, 0.2, 100)

