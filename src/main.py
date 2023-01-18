# import datetime
import time
import logging
import settings
import hookup

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger("extract-dspace-loop")

runs = settings.LIMIT_RUN

while runs != 0:
    # count down if there is a termination flag. 
    if runs > 0:
        runs -= 1

    logger.info("start iteration")
    hookup.run()
    # implicit timing
    logger.info("finish iteration") 
    time.sleep(settings.BATCH_INTERVAL)
