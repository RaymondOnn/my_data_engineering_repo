import pytest
import os
import httpx
from components.extract.src.extract.scraper import StaticScraper, NoMatchFound, InvalidScraperParams
from unittest.mock import Mock, patch, create_autospec

workdir = os.path.dirname(os.path.abspath(__file__))
first_result_page_path = os.path.join(workdir, 'First_Result_Page.html')
product_page = os.path.join(workdir, 'Product_Page.html')
get_value_params = [
    ('text', 'div.product_main > h1', 0, 'A Light in the Attic'),  # title
    ('text', 'table.table-striped tr:nth-child(6) > td', 0, 'In stock (22 available)'),  # stock
    ('text', 'table.table-striped tr:nth-child(1) > td', 0, 'a897fe39b1053632'),  # sku
    ('text', 'p.price_color', 0, '£51.77'),  # price
    ('class', 'p.star-rating', 0, 'star-rating Three')
]


@pytest.fixture(scope='session')
def scraper():
    return StaticScraper('')


@pytest.fixture()  # indicate curr function is a fixture
def result_response():
    return open(first_result_page_path, 'r').read()


@pytest.fixture()  # indicate curr function is a fixture
def product_response():
    return open(product_page, 'r').read()


def test_parse_text_invalid_resp():
    pass


def test_init():
    test_url = 'http://www.testurl.com'
    ss = StaticScraper(url=test_url)
    assert isinstance(ss.client, httpx.Client)
    assert ss.base_url == test_url
    assert ss.headers is None


# def test_fetch_response():
#     test_url = 'http://www.testurl.com'
#     mock_client = create_autospec(httpx.Client(), instance=True)
#     mock_scraper = StaticScraper(url=test_url)
#     mock_scraper.client = mock_client
#     mock_scraper.fetch_response()
#     assert mock_scraper.client == mock_client
#     mock_client.get.assert_called_once_with(test_url, None)


def test_get_nodes_invalid_selector(scraper, product_response):
    with pytest.raises(InvalidScraperParams):
        scraper.get_nodes(product_response, 'article.product_pod> h3 a')


def test_get_value_no_match_found(scraper, product_response):
    with pytest.raises(NoMatchFound):
        scraper.get_value(product_response, 'text', 'does-not-exist', 0)


def test_get_value_index_gt_num_nodes(scraper, product_response):
    with pytest.raises(NoMatchFound):
        scraper.get_value(product_response, 'text', 'p.star-rating', 1)


def test_get_value_invalid_target_value(scraper, product_response):
    with pytest.raises(InvalidScraperParams):
        scraper.get_value(product_response, 'test', 'p.star-rating', 0)


def test_get_value_invalid_selector(scraper, product_response):
    with pytest.raises(InvalidScraperParams):
        scraper.get_value(product_response, 'class', 'p.star-rating>', 0)


def test_get_nodes_valid_resp(scraper, result_response):
    nodes = scraper.get_nodes(result_response, 'article.product_pod > h3 a')
    assert isinstance(nodes, list)


def test_parse_product_links_valid_resp(scraper, result_response):
    nodes = scraper.get_nodes(result_response, 'article.product_pod > h3 a')
    link = 'catalogue/' + nodes[0].attributes['href'].split('catalogue/')[-1]
    parts = link.split('/')
    assert len(parts) == 3
    assert parts[-1] == 'index.html'


@pytest.mark.parametrize('target_val, selector, index, expected', get_value_params)
def test_get_value_valid_resp(scraper, product_response, target_val, selector, index, expected):
    text = scraper.get_value(product_response, target_val, selector, index)
    assert text == expected
