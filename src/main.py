import time
import logging
import settings
import hookup
import asyncio

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)

logger = logging.getLogger('extract-dspace-loop')

limit_batch = settings.LIMIT_BATCH  # -1, no limit ... process all batches

async def mainLoop():
    batch_count = 0
    resumption_token = None

    while (limit_batch == -1) or (limit_batch > 0 and batch_count < limit_batch): # limit number of batches to be processed:
        logger.info('start iteration') # for server logs and profiling, need to run right before the hookup.run().
        resumption_token = await hookup.run(resumption_token) # ask for a batch of records and add them to the graph database
        logger.info('complete iteration') # for server logs and profiling, need to run right after the hookup.run().

        # house keeping
        batch_count += 1 # increment batch counter
        
        # resumption_token = None if there are no more batches to be processed
        if resumption_token is None:
            logger.info('finish iteration after ' + str(batch_count) + ' batches') 
            sleepTimeout = settings.PUBDB_UPDATE_INTERVAL
            batch_count = 0 # reset batch counter for
        else:
            logger.info('prepare for another batch') 
            sleepTimeout = settings.OAI_REQUEST_INTERVAL # wait before asking for the next batches
        
        time.sleep(sleepTimeout) # wait before asking for the next batches

# run the main loop
asyncio.run(mainLoop)
