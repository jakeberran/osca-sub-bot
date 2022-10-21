from datetime import datetime
import logging

import azure.functions as func


def main(timer: func.TimerRequest) -> None:
    logging.info('Started function')
    utc_timestamp = datetime.now(datetime.timezone.utc).isoformat()

    if timer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)