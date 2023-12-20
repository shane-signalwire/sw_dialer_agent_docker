#!/usr/bin/env python3

import logging
import os
import sqlite3
import time
from signalwire.relay.consumer import Consumer

class CustomConsumer(Consumer):
  def setup(self):
    self.project = os.environ.get('PROJECT', None)
    self.token = os.environ.get('TOKEN', None)
    self.contexts = ['dialer']

  async def ready(self):
    logging.info('Dialer App Consumer Ready')
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()

    # Create the dialto table if it doesn't exist
    dialto_table = """ CREATE TABLE if not exists dialto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        to_num TEXT NOT NULL,
        from_num TEXT NOT NULL,
        amd_result TEXT
        );"""

    cursor.execute(dialto_table)
    db.commit()

    while True:
        to_num = ""
        from_num = ""

        results = cursor.execute(
            "SELECT id, to_num, from_num from dialto where amd_result is null limit 1"
        ).fetchall()

        # TODO: Turn off logging to save disk/memory space
        if len(results) == 0:
            logging.info ('nothing to do')
            time.sleep(3)

        else:
            for i, t, f in results:
                id = i
                to_num = t
                from_num = f

            logging.info(f'{to_num}: Dialing destination number')
            dial_result = await self.client.calling.dial(to_number=to_num, from_number=from_num)
            if dial_result.successful is False:
                logging.info(f'{to_num}: Outboud call failed.')
                cursor.execute(
                    "UPDATE dialto set amd_result = \"call failed\" where id = ?",
                    (id,)
                )
                
            amd = await dial_result.call.amd(wait_for_beep=True)
            # "pop" the record from the database; i.e. update the record with the amd result.
            amd_result = amd.result
            cursor.execute(
                "UPDATE dialto set amd_result = ? where id = ?",
                (amd_result, id,)
            )
            db.commit()

            if amd.successful and amd.result =='MACHINE':
                logging.info(f'{to_num}: {amd.result}')
                logging.info(f'{to_num}: Leaving Voicemail')
                await dial_result.call.play_tts(text='Sorry we missed you.  We will call back later!')

            if amd.successful and amd.result == 'HUMAN':
                logging.info(f'{to_num}: {amd.result}')
                logging.info(f'{to_num}: Playing Message to user')
                #await dial_result.call.play_tts(text='This is a company calling you back.  Placing you in the queue for an agent')
                agent_dest = self.project = os.environ.get('AGENT_DEST', None)
                devices = [
                  { 'to_number': agent_dest, 'timeout': 15 }
                ]
                await dial_result.call.connect(device_list=devices)

            #await dial_result.call.hangup()
            #logging.info('The call has hung up')

  def teardown(self):
    logging.info('Consumer teardown..')

consumer = CustomConsumer()
consumer.run()