import unittest
from unittest.mock import patch, MagicMock
from src import service


class TestService(unittest.TestCase):
    @patch('mongo_client.get_default_language_collection')
    def test_update_language(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.update_one.return_value.matched_count = 1

        result = service.update_language(1, 'fr')
        self.assertEqual(result, 1)
        mock_collection.update_one.assert_called_once()

    @patch('mongo_client.get_default_language_collection')
    def test_get_language_by_key(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = {'key': 1, 'language': 'fr'}

        language = service.get_language_by_key(1)
        self.assertEqual(language, 'fr')

        mock_collection.find_one.return_value = None
        language = service.get_language_by_key(2)
        self.assertEqual(language, 'en')

    @patch('mongo_client.get_daily_stats_collection')
    def test_increment_daily_stats(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        mock_collection.update_one.return_value.matched_count = 1
        mock_collection.find_one.return_value = {'_id': 1, 'amount': 5}
        result = service.increment_daily_stats('en', '2024-02-08')
        self.assertEqual(result, 1)

        mock_collection.find_one.return_value = None
        result = service.increment_daily_stats('en', '2024-02-09')
        self.assertEqual(result, 1)

    @patch('mongo_client.get_daily_stats_collection')
    def test_get_daily_stats(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = {'amount': 10}

        amount = service.get_daily_stats('en', '2024-02-08')
        self.assertEqual(amount, 10)

        mock_collection.find_one.return_value = None
        amount = service.get_daily_stats('en', '2024-02-09')
        self.assertEqual(amount, 0)

    @patch('mongo_client.get_recent_events_collection')
    def test_append_event(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find.return_value.sort.return_value = []

        event: dict[str, str] = {
            'title': 'Event 1',
            'user': 'User1',
            'timestamp': '2024-02-08T12:00:00Z',
            'server_url': 'http://localhost'
        }
        service.append_event('en', event)
        mock_collection.insert_one.assert_called_once()

        mock_collection.find.return_value.sort.return_value = [{'_id': i} for i in range(10)]
        mock_collection.delete_one.return_value = None
        service.append_event('en', event)

    @patch('mongo_client.get_recent_events_collection')
    def test_get_events(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find.return_value = [{'title': 'Event 1'}, {'title': 'Event 2'}]

        events = service.get_events('en')
        self.assertEqual(len(events), 2)


if __name__ == '__main__':
    unittest.main()
