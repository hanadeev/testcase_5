#!/srv/anaconda3/bin/python3.7

import asyncio
import motor.motor_asyncio
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
import json
import logging
import projectconf as cf

logging.disable(logging.CRITICAL)
# logging.basicConfig(level=logging.DEBUG)


class DataBase:
    """ Layer for working with a remote database of sold cars """
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient()
        logging.debug("Base client: {}".format(self.client))
        self.db = self.client.main_database
        self.coll = self.db.sold_cars

    async def insert(self, document: dict) -> dict:
        # Because of argument passed in ObjectId() must be a string of 24 hex characters,
        # then add a string with serialNumber with 'f' to 24 characters
        # Note: serialNumber is always shorter then 24 characters/digits (2^64)
        fill_id = '{:f<24}'.format(document['serialNumber'])
        document['_id'] = ObjectId(fill_id)
        try:
            insert_result = await self.coll.insert_one(document)
        except PyMongoError as e:
            logging.error("PyMongoError: {}".format(e.args))
            return {'state': 'failed'}
        logging.debug('Insert result into the base: {}'.format(insert_result))
        return {'state': 'success'}

    async def get(self, id_: int) -> dict:
        # Because of argument passed in ObjectId() must be a string of 24 hex characters,
        # then add a string with serialNumber with 'f' to 24 characters
        fill_id = '{:f<24}'.format(id_)
        try:
            query_result = await self.coll.find_one({'_id': ObjectId(fill_id)})
            if query_result is not None:
                query_result.pop('_id')     # Delete database service key
            else:
                query_result = {'state': 'failed'}
        except PyMongoError as e:
            logging.error("PyMongoError: {}".format(e.args))
            return {'state': 'failed'}
        logging.debug('Query result in the base: {}'.format(query_result))
        return query_result


class ServerCarCenter:
    """Class for creation and running TCP Socket Server, and for connection to database
    usage:
        s = server.Server()
        s.start()
    """
    def __init__(self, host: str = cf.host, port: int = cf.port):
        self.host = host
        self.port = port
        self.db = DataBase()

    def start(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_request, self.host, self.port, loop=loop)
        try:
            server = loop.run_until_complete(coro)
        except OSError as e:
            print('Error. Address already in use ({}:{})'.format(self.host, self.port))
            logging.error("OSError: {}".format(e.args))
            return
        print('Start server on {}'.format(server.sockets[0].getsockname()))
        # Serve requests until Ctrl+C is pressed
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('KeyboardInterrupt. Exit')
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

    async def handle_request(self, reader, writer):
        """
        API
        1. request: {'get': 'properties_form'} - template request for new sold car
            answer: see projectconf.default_form
        2. request: {'get': 'car', 'serialNumber': int}
            answer: dict with info about car or {'state': 'failed'}
        3. request: {'insert': {dict with properties}}
            answer: {'state': 'failed' | 'success'}
        4. request: {'close': 1}
            No answer, just close connection
        """
        try:
            addr = writer.get_extra_info('peername')
            while True:
                data = None
                request_b = await reader.read(cf._max_buffer)
                request = cf.decode(request_b)
                logging.debug('Server received from {}: {}'.format(addr, request))
                keys_ = request.keys()

                if 'get' in keys_:
                    if request['get'] == 'properties_form':
                        data = cf.default_form
                    elif request['get'] == 'car' and 'serialNumber' in keys_:
                        data = await self.get_car(request['serialNumber'])
                elif 'insert' in keys_:
                    data = await self.insert_car(request['insert'])

                elif 'close' in keys_:
                    writer.close()
                    await writer.wait_closed()
                    break

                if not data:
                    continue

                writer.write(cf.encode(data))
                logging.debug('Server send to {}: {}'.format(addr, data))
                await writer.drain()

        except ConnectionResetError as e:
            print('Connection reset by peer')
            logging.error("ConnectionResetError: {}".format(e.args))
            writer.close()
            await writer.wait_closed()
        except json.decoder.JSONDecodeError as e:
            print('Uncorrected format')
            logging.error("JSONDecodeError: {}".format(e.args))
            writer.close()
            await writer.wait_closed()

        finally:
            print("Closed connection from {}".format(addr))

    async def get_car(self, id_: int) -> dict:
        result = await self.db.get(id_)
        return result

    async def insert_car(self, properties: dict) -> dict:
        result = await self.db.insert(properties)
        return result
