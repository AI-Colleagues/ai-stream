"""AWS related classes and functions."""

import json
import os
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from ai_stream import LOCAL_AWS
from ai_stream.config import get_logger
from ai_stream.config import load_config


PYNAMODB_TABLES: dict[str, type[Model]] = {}
logger = get_logger(__name__)
config = load_config()


def register_pynamodb_table(cls: type[Model]) -> type[Model]:
    """Register a PynamoDB table."""
    PYNAMODB_TABLES[cls.__name__] = cls
    return cls


class DefaultTableMeta:
    """Default table meta for all PynamoDB Model meta."""

    host = config.moto_url if LOCAL_AWS else None


@register_pynamodb_table
class PromptsTable(Model):
    """Table for storing prompts."""

    class Meta(DefaultTableMeta):
        """Table meta."""

        table_name = config.dynamodb.prompts_table

    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute(range_key=True)
    value = UnicodeAttribute()


def _prepare_dev_env() -> None:
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


def create_tables() -> None:
    """Create all defined tables if they don't exist yet."""
    if LOCAL_AWS:
        _prepare_dev_env()

    for table_name, table_class in PYNAMODB_TABLES.items():
        if not table_class.exists():
            table_class.create_table(
                wait=True, billing_mode=config.dynamodb.billing_mode
            )
            logger.info(f"Table {table_name} created successfully.")


def dump_data_to_disk() -> None:
    """Dump DynamoDB data to disk."""
    if not LOCAL_AWS:
        return
    data = {}
    for table_name, table_class in PYNAMODB_TABLES.items():
        items = table_class.scan()
        data[table_name] = [item.to_simple_dict() for item in items]

    with open(config.data_dump_file_name, "w") as f:
        json.dump(data, f)

    logger.info(f"Data dumped to file {config.data_dump_file_name}.")


def load_data_from_disk() -> None:
    """Load DynamoDB dump from disk."""
    if not LOCAL_AWS:
        return
    if os.path.exists(config.data_dump_file_name):
        with open(config.data_dump_file_name) as f:
            data = json.load(f)
            for table_name, items in data.items():
                table_class = PYNAMODB_TABLES.get(table_name)
                if table_class:
                    with table_class.batch_write() as batch:
                        for item_data in items:
                            item = table_class(**item_data)
                            batch.save(item)

    logger.info(f"Loaded data from file {config.data_dump_file_name}.")
