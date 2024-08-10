import logging
from typing import Any, Callable
import sys

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from sdk.exceptions import YandexException

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def retry_n_times(max_retries: int) -> Callable[[Any], Any]:
    """Retry decorator. Calls decorated function until amount of unsuccessful attempts is equal to {max_retries}"""

    retry_conditions = retry_if_exception_type(YandexException)
    min_delay_seconds = 1
    max_delay_seconds = 128

    # Wait 2^{retry_number} second between each retry starting with
    # {min_delay_seconds} seconds, then up to {max_delay_seconds} seconds, then {max_delay_seconds} seconds afterward
    return retry(
        reraise=True,
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=2, min=min_delay_seconds, max=max_delay_seconds),
        retry=retry_conditions,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )

