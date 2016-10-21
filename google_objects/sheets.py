# -*- coding: utf-8 -*-

"""

Google Sheets API
    Mon Sep 19 21:10:28 2016

"""

import re
import logging
from decimal import Decimal, InvalidOperation

from . import GoogleAPI, GoogleObject
from .utils import keys_to_snake

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO:
    # i/ ensure all cell data reflects table row insertion and deletion
    # ii/ page title and descriptor need to be found and initialized
    # iii/ change .from_existing to .from_raw


class SheetsAPI(GoogleAPI):

    """Creates a Google Sheets Resource"""

    def __init__(self, credentials):
        """Google Drive API client, exposes
        collection resources
        """
        super(self.__class__, self).__init__(credentials)
        self._resource = self.build('sheets', 'v4')

    def get_spreadsheet(self, id):
        """Returns a Spreadsheet Object

        :id: Spreadsheet ID
        :returns: <Spreadsheet> Model

        """
        data = self._resource.spreadsheets().get(
            spreadsheetId=id
        ).execute()

        return Spreadsheet.from_existing(data, self)


    def get_values(self, spreadsheet_id, range_name):
        """Initialize a new block and return it"""

        data = self._resource.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        return Block.from_existing(data, client=self)

    def push_updates(self, spreadsheet_id, updates):
        spreadsheets = self._resource.spreadsheets()
        spreadsheets.batchUpdate(
            presentationId = spreadsheet_id,
            body={'requests': updates}
        )
        spreadsheets.execute()


"""
    Sheets Objects:
        i/ Spreadsheet
        ii/ Sheet
        iii/ Block
"""

class Spreadsheet(GoogleObject):

    """Represents a Google API Spreadsheet object"""

    def __init__(self, client=None, **kwargs):
        """Creates a new Spreadsheet Object"""

        self.client = client
        self.__updates = []

        # initalize the other properties
        super(self.__class__, self).__init__(**kwargs)

    @classmethod
    def from_existing(cls, data, client=None):
        """initiates using existing Spreadsheet resource"""

        new_data = keys_to_snake(data)
        return cls(client, **new_data)

    def __iter__(self):
        for sheet in self.sheets:
            yield sheet

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.__updates:
            self.client.push_updates(self._id, self._updates)
            # TODO: add success handlers
            del self._updates[:]

    @property
    def id(self):
        return self._spreadsheet_id

    @property
    def title(self):
        return self._properties.get('title')

    @title.setter
    def title(self, value):
        self._properties['title'] = value

    @property
    def sheets(self):
        return [Sheet.from_existing(each, self) for each in self._sheets]

    def named_ranges(self):
        return self._named_ranges

    def get_range(self, sheet_range):
        """Takes a sheet range and initializes a block object
        with the raw data and the spreadsheet for update
        functionality.
        """
        return self.client.get_values(self.id, sheet_range)


class Sheet(GoogleObject):

    """Represents a Google API Sheet object,
    there is little functionality associated with
    this object, it will be mostly used as reference for
    initializing blocks.
    """

    def __init__(self, spreadsheet=None, **kwargs):
        """Creates a new Sheet Object"""
        self.spreadsheet = spreadsheet

        # initalize the other properties
        super(self.__class__, self).__init__(**kwargs)

        self.properties = kwargs.get('properties', {})

    @classmethod
    def from_existing(cls, data, spreadsheet):
        """initiates using existing Sheet resource"""

        new_data = keys_to_snake(data)
        return cls(spreadsheet, **new_data)

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        if 'sheet_id' in value:
            self._properties['sheet_id'] = value['sheet_id']

        if 'title' in value:
            self._properties['title'] = value['title']

    @property
    def id(self):
        return self._properties.get('sheet_id')

    @property
    def title(self):
        return self._properties.get('title')

    @title.setter
    def title(self, value):
        self._properties['title'] = value

    def values(self, start=None, end=None):
        """Returns <Block> consisting of all sheet data"""

        block = self.spreadsheet.get_range(self.title)
        block.spreadsheet = self.spreadsheet

        return block


class Block(GoogleObject):

    """Recieves a dictionary corresponding to a
    ValueRange in Google Sheets and provides methods related
    to modification and formatting.
    """

    def __init__(self, client=None, spreadsheet=None, **kwargs):
        self.client = client
        self.spreadsheet = spreadsheet

        # initalize the other properties
        super(self.__class__, self).__init__(**kwargs)

    @classmethod
    def from_existing(cls, data, client, spreadsheet=None):
        """initiates using existing ValueRange resource"""

        new_data = keys_to_snake(data)
        return cls(client, spreadsheet, **new_data)

    def __iter__(self):
        for row in self._values:
            yield [self.Cell(self, val) for val in row]

    def map(self, func):
        """Returns <Decimal> of block sum"""
        for row in self._rows:
            for cell in row:
                cell.value = func(cell)

    @property
    def is_numerical(self):
        for row in self._values:
            for val in row:
                cell = self.Cell(self, val)
                if not cell.is_numerical:
                    return False
        return True

    class Cell(object):

        """Represents a Google Sheets Cell, each value
        is initially <unicode>
        """

        def __init__(self, block, value):
            self._block = block
            self.value = value

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return self.value.encode('utf-8').strip()

        @property
        def is_numerical(self):
            """Determines if value is a number, removes
            '$', ',', '.' in case of financial formatting.
            """
            try:
                Decimal(self.value)
                return True
            except InvalidOperation:
                return False

        def make_numerical(self):
            self.value = re.sub(r'[^\d.]', '', self.value)

        def match(self, regex):
            """Returns True or False if regular expression
            matches the text inside.
            """
            if self.value and re.match(regex, self.value):
                return True
            return False
