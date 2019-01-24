""" Functionality related to the import command """

import argparse
import bz2
import csv
import gzip
import io
import json
from itertools import islice

import progressbar

from trade_companion import models
from trade_companion.cmd import SUB_COMMAND_PARSER

IMPORT_PARSER = SUB_COMMAND_PARSER.add_parser(
    'import', aliases=['im'],
    help="Import data from various files.")

_ENTITIES = [c for c in models.Base.__subclasses__()]


def _entity_lookup(entity_name):
    entity_name = entity_name.lower()
    for entity in _ENTITIES:
        if entity_name == entity.__name__.lower():
            return entity

    return None


IMPORT_PARSER.add_argument(
    "entity", action="store", metavar="ENTITY", type=_entity_lookup,
    choices=_ENTITIES,
    help=('The "root"-entity in the file. Valid choices are: %s'
          % ', '.join(sorted(c.__name__ for c in _ENTITIES))))

IMPORT_PARSER.add_argument(
    "input_file", action="store", type=argparse.FileType(mode="rb"), metavar="INPUT",
    help="The file to read system data from.")

DECOMPRESSION_OPTIONS = IMPORT_PARSER.add_argument_group(
    title="decompression options")
DECOMPRESSION_OPTIONS.add_argument(
    "--bz2", action="store_const", const=lambda fp: bz2.BZ2File(filename=fp),
    help="Inputfile is compressed with bzip2.", dest="decompressor")
DECOMPRESSION_OPTIONS.add_argument(
    "--gz", action="store_const", const=lambda fp: gzip.GzipFile(fileobj=fp),
    help="Inputfile is compressed with gzip.", dest="decompressor")

FORMAT_OPTIONS = IMPORT_PARSER.add_argument_group(
    title="input format options")
FORMAT_OPTIONS.add_argument(
    "--csv", action="store_const", const=csv.DictReader,
    help="Inputfile is a csv-file.", dest="input_format")
FORMAT_OPTIONS.add_argument(
    "--jsonl", action="store_const", const=lambda fp: map(json.loads, fp),
    help="Inputfile is a line-delimited json-file.", dest="input_format")

DATABASE_OPTIONS = IMPORT_PARSER.add_argument_group(
    title="database options",
    description=("These options affect the interaction with the"
                 " underlying database instance."))
DATABASE_OPTIONS.add_argument(
    "--db-type", action="store", type=str, choices=["sqlite"],
    default="sqlite", help="The type of the database")
DATABASE_OPTIONS.add_argument(
    "--batch-size", action="store",
    type=int, default=20000, metavar="BATCH_SIZE",
    help="The batch size to use for commiting data to database. Default")


def chunked(iterable, chunk_size):
    """ Return iterable chunks from an iterator.

    This sort of works like a grouping in a fixed size.
    """
    while True:
        chunk = islice(iterable, chunk_size)
        yield chunk


def model_import(options: argparse.Namespace):
    """ Import instances of  model_class from filename

    The filename right now needs to be a bzip2-compressed csv-file
    where the first row contains the names of the attributes.
    """
    model_class = options.entity
    print("Importing %s from: %s"
          % (model_class.__tablename__, options.input_file.name))

    chunk_size = options.chunk_size
    decompressor = options.decompressor
    deserializer = options.input_format

    io_file = options.input_file
    with io_file:
        io_file.seek(0, io.SEEK_END)
        file_size = io_file.tell()
        io_file.seek(0, io.SEEK_SET)

        if decompressor:
            io_wrapper = io.TextIOWrapper(decompressor(io_file),
                                          encoding="utf-8")
        else:
            io_wrapper = io.TextIOWrapper(io_file, encoding="utf-8")

        dict_transform = model_class.to_filtered_dict

        with io_wrapper, \
                progressbar.ProgressBar(max_value=file_size) as progress:

            for chunk in chunked(deserializer(io_wrapper), chunk_size):
                chunk_systems = list(map(dict_transform, chunk))
                if not chunk_systems:
                    break

                models.engine.execute(model_class.__table__.insert(),
                                      chunk_systems)
                progress.update(io_file.tell())


IMPORT_PARSER.set_defaults(func=model_import)
