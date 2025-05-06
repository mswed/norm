import pytest
from unittest.mock import patch
import norm_the_orm as norm
from .mock_shotgrid import MockFlow


@pytest.fixture
def mock_flow():
    """
    A mock Flow instance. Flow is used to connect to SG.
    """
    mock = MockFlow()
    return mock


@pytest.fixture
def mock_session(mock_flow):
    """
    Patch Flow.connect and set up a Norm session
    """
    with patch('shotgrid_flow.Flow.connect', return_value=mock_flow):
        # Set up a new session
        session = norm.Session.new()
        yield session
