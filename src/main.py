import time
import logging
import settings
import hookup

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger('extract-dspace-loop')

limit_batch = settings.LIMIT_BATCH  # -1, no limit ... process all batches
batch_count = 0
resumption_token = None

while (limit_batch == -1) or (limit_batch > 0 and batch_count < limit_batch): # limit number of batches to be processed:
    logger.info('start iteration') # for server logs and profiling, need to run right before the hookup.run().
    resumption_token = await hookup.run(resumption_token) # ask for a batch of records and add them to the graph database
    # resumption_token = None if there is only a single batch to be processed
    logger.info('complete iteration') # for server logs and profiling, need to run right after the hookup.run().
    
    # house keeping
    batch_count += 1 # increment batch counter
    time.sleep(settings.OAI_REQUEST_INTERVAL) # wait before asking for the next batches
    if resumption_token is None:
        logger.info('finish iteration after ' + str(batch_count) + ' batches') 
        time.sleep(settings.PUBDB_UPDATE_INTERVAL)
        batch_count = 0 # reset batch counter for
