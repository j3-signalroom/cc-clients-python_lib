from typing import Final


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__credits__    = ["Jeffrey Jonathan Jennings"]
__license__    = "MIT"
__maintainer__ = "Jeffrey Jonathan Jennings"
__email__      = "j3@thej3.com"
__status__     = "dev"


DEFAULT_REQUEST_TIMEOUT_IN_SECONDS: Final[int] = 30
DEFAULT_PAGE_SIZE: Final[int] = 10

# Query Parameters.
QUERY_PARAMETER_PAGE_SIZE = "page_size"
QUERY_PARAMETER_PAGE_TOKEN = "page_token"
