try:
    from typing import Any
    from urllib.parse import urljoin

    import httpx
    from selectolax.parser import HTMLParser, Node
    from utils.logger import get_logger
except ImportError as err:
    print("[Error]: Failed to import {}.".format(err.args[0]))
except Exception as e:  # handle all other errors
    print(e)

logger = get_logger(__name__)


class InvalidScraperParams(Exception):
    pass


class NoMatchFound(Exception):
    pass
    # def __init__(self, msg):
    #     self.msg = msg
    #     print('NoMatchFound: E')


def log_request(request):
    logger.info(f"Request event hook: {request.method} {request.url} - Waiting for response")


def log_response(response):
    request = response.request
    logger.info(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

class StaticScraper:
    def __init__(self, url: str, headers: dict[str, Any] = None):
        self.headers = headers
        self.client = httpx.Client(event_hooks={'request': [log_request], 'response': [log_response]})
        self.base_url = url

    def fetch_response(self, page_header: str = None):
        try:
            resp = self.client.get(urljoin(self.base_url, page_header), headers=self.headers)
            resp.raise_for_status()
            return resp.text
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url!r}.")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        # finally:
        #     self.client.close()

    @staticmethod
    def get_nodes(response: str, selector: str) -> list[Node]:
        try:
            html = HTMLParser(response)
            return html.css(selector)
        except (TypeError, ValueError) as err_msg:
            raise InvalidScraperParams(err_msg)

    def get_value(self, response: str, target_value: str, selector: str, index: int):
        try:
            nodes: list[Node] = self.get_nodes(response, selector)
            if not nodes:
                logger.info('No matching element/attribute was found.')
                return None
            if target_value == 'text':
                return nodes[index].text(strip=True)
            if target_value == 'html':
                return nodes[index].html
            return nodes[index].attributes[target_value]
        except (TypeError, ValueError, KeyError) as err_msg:
            raise InvalidScraperParams(err_msg)
        except IndexError as err_msg:
            raise NoMatchFound(f'Index used was too large. Only {len(nodes)} nodes were found.')
