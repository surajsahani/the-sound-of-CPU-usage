import pytest
from unittest import mock
import psutil
from midiutil import MIDIFile
from the_sound_of_cpu_usage import clamp, genNote

@pytest.fixture
def mock_psutil_cpu_percent():
    with mock.patch('psutil.cpu_percent') as mock_cpu_percent:
        mock_cpu_percent.side_effect = lambda interval, percpu: [50] * psutil.cpu_count()  # Mock CPU usage at 50%
        yield mock_cpu_percent

@pytest.fixture
def mock_midi_file():
    with mock.patch('midiutil.MIDIFile') as mock_midi:
        mock_midi_instance = mock.Mock()
        mock_midi.return_value = mock_midi_instance
        yield mock_midi_instance

@pytest.fixture
def setup_mocks(mock_psutil_cpu_percent, mock_midi_file):
    # Mock the necessary methods and attributes
    mock_midi_file.addTempo.return_value = None
    mock_midi_file.addTrackName.return_value = None
    mock_midi_file.addNote.return_value = None

    yield

# happy_path - test_clamp_value_within_range - Test that clamp function returns the value when it is within the range.
def test_clamp_value_within_range():
    result = clamp(5, 1, 10)
    assert result == 5

# happy_path - test_clamp_value_below_range - Test that clamp function returns the smallest value when the input is less than the smallest.
def test_clamp_value_below_range():
    result = clamp(0, 1, 10)
    assert result == 1

# happy_path - test_clamp_value_above_range - Test that clamp function returns the largest value when the input is greater than the largest.
def test_clamp_value_above_range():
    result = clamp(15, 1, 10)
    assert result == 10

# happy_path - test_gennote_first_core - Test that genNote function generates a note with correct pitch and duration for the first CPU core.
def test_gennote_first_core(setup_mocks, mock_psutil_cpu_percent, mock_midi_file):
    genNote(0, 0, 0)
    pitch = int(mock_psutil_cpu_percent.return_value[0]) + 15
    duration = clamp(round(int(mock_psutil_cpu_percent.return_value[0]) % 3, 2), 0.2, 2.5)
    mock_midi_file.addNote.assert_called_with(0, 0, pitch, 1, duration, 100)

# happy_path - test_gennote_last_core - Test that genNote function generates a note with correct pitch and duration for the last CPU core.
def test_gennote_last_core(setup_mocks, mock_psutil_cpu_percent, mock_midi_file):
    genNote(3, 3, 3)
    pitch = int(mock_psutil_cpu_percent.return_value[3]) + 15
    duration = clamp(round(int(mock_psutil_cpu_percent.return_value[3]) % 3, 2), 0.2, 2.5)
    mock_midi_file.addNote.assert_called_with(3, 0, pitch, 1, duration, 100)

# edge_case - test_clamp_negative_value - Test that clamp function handles negative values correctly by clamping to the smallest value.
def test_clamp_negative_value():
    result = clamp(-5, 0, 10)
    assert result == 0

# edge_case - test_clamp_zero_value - Test that clamp function handles zero correctly when within the range.
def test_clamp_zero_value():
    result = clamp(0, -10, 10)
    assert result == 0

# edge_case - test_gennote_core_index_out_of_range - Test that genNote function handles CPU core index out of range by using the first core.
def test_gennote_core_index_out_of_range(setup_mocks, mock_psutil_cpu_percent, mock_midi_file):
    genNote(8, 8, 0)
    pitch = int(mock_psutil_cpu_percent.return_value[0]) + 15
    duration = clamp(round(int(mock_psutil_cpu_percent.return_value[0]) % 3, 2), 0.2, 2.5)
    mock_midi_file.addNote.assert_called_with(0, 0, pitch, 1, duration, 100)

# edge_case - test_gennote_max_cpu_usage - Test that genNote function handles maximum CPU usage by generating maximum pitch and duration.
def test_gennote_max_cpu_usage(setup_mocks, mock_psutil_cpu_percent, mock_midi_file):
    with mock.patch('psutil.cpu_percent', return_value=[100] * psutil.cpu_count()):
        genNote(0, 0, 0)
        pitch = 115
        duration = 2.5
        mock_midi_file.addNote.assert_called_with(0, 0, pitch, 1, duration, 100)

# edge_case - test_gennote_min_cpu_usage - Test that genNote function handles minimum CPU usage by generating minimum pitch and duration.
def test_gennote_min_cpu_usage(setup_mocks, mock_psutil_cpu_percent, mock_midi_file):
    with mock.patch('psutil.cpu_percent', return_value=[0] * psutil.cpu_count()):
        genNote(0, 0, 0)
        pitch = 15
        duration = 0.2
        mock_midi_file.addNote.assert_called_with(0, 0, pitch, 1, duration, 100)

