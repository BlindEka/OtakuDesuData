import unittest
from unittest.mock import patch, MagicMock
from otakudesudata import search, get_ongoing, get_schedules, get_anime_list  # Ensure correct library name
from otakudesudata.parser import SearchResultParser, AnimeParser, BatchParser, EpisodeParser, OngoingParser
# Removed unused imports

class TestSearchFunction(unittest.TestCase):
    @patch('httpx.get')
    def test_search(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        results = search('naruto')
        self.assertIsInstance(results, dict)

class TestGetOngoingFunction(unittest.TestCase):
    @patch('otakudesudata.parser.OngoingParser')
    def test_get_ongoing(self, mock_ongoing_parser):
        mock_ongoing_parser.return_value = MagicMock()
        ongoing = get_ongoing()
        self.assertIsNotNone(ongoing)

    @patch('otakudesudata.parser.OngoingParser')
    def test_get_ongoing_all(self, mock_ongoing_parser):
        mock_ongoing_parser.return_value = MagicMock()
        ongoing = get_ongoing(get_all=True)
        self.assertIsInstance(ongoing, list)

class TestGetSchedulesFunction(unittest.TestCase):
    @patch('httpx.get')
    def test_get_schedules(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        schedules = get_schedules()
        self.assertIsInstance(schedules, dict)

class TestGetAnimeListFunction(unittest.TestCase):
    @patch('httpx.get')
    def test_get_anime_list(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        anime_list = get_anime_list()
        self.assertIsInstance(anime_list, list)

class TestSearchResultParser(unittest.TestCase):
    def test_parser_initialization(self):
        html_string = '<html></html>'
        parser = SearchResultParser(html_string)
        self.assertIsInstance(parser, SearchResultParser)

class TestAnimeParser(unittest.TestCase):
    @patch('httpx.get')
    def test_anime_parser_initialization(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        parser = AnimeParser('https://example.com')
        self.assertIsInstance(parser, AnimeParser)

class TestBatchParser(unittest.TestCase):
    @patch('httpx.get')
    def test_batch_parser_initialization(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        parser = BatchParser('https://example.com')
        self.assertIsInstance(parser, BatchParser)

class TestEpisodeParser(unittest.TestCase):
    @patch('httpx.get')
    def test_episode_parser_initialization(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        parser = EpisodeParser('https://example.com')
        self.assertIsInstance(parser, EpisodeParser)

class TestOngoingParser(unittest.TestCase):
    @patch('httpx.get')
    def test_ongoing_parser_initialization(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        parser = OngoingParser('https://example.com')
        self.assertIsInstance(parser, OngoingParser)

if __name__ == '__main__':
    unittest.main()