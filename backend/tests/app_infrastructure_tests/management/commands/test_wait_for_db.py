from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


@patch('app_infrastructure.management.commands.wait_for_db.Command.check')
class TestWaitForDBCommand:
    """Tests for wait_for_db admin command."""

    def test_wait_for_db_ready(self, patched_check: MagicMock):
        """
        GIVEN: Already running database.
        WHEN: wait_for_db command called.
        THEN: wait_for_db called once with success.
        """
        # Overrides value returned from function mocked in @patch decorator
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep: MagicMock, patched_check: MagicMock):
        """
        GIVEN: Starting database.
        WHEN: wait_for_db command called.
        THEN: wait_for_db called 6 times before finally connect.
        """
        patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        assert patched_check.call_count == 6
        patched_check.assert_called_with(databases=['default'])
