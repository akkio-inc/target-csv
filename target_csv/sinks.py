"""CSV target sink class, which handles writing streams."""

import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytz
from singer_sdk import PluginBase
from singer_sdk.sinks import BatchSink

from target_csv.serialization import write_csv, write_csv_header, write_csv_rows


class CSVSink(BatchSink):
    """CSV target sink class."""

    @property
    def max_size(self) -> int:
        # base sink attribute that determines max batch size
        return 1_000

    _wrote_header: bool = False

    def __init__(  # noqa: D107
        self,
        target: PluginBase,
        stream_name: str,
        schema: Dict,
        key_properties: Optional[List[str]],
    ) -> None:
        self._timestamp_time: Optional[datetime.datetime] = None
        super().__init__(target, stream_name, schema, key_properties)

    @property
    def timestamp_time(self) -> datetime.datetime:  # noqa: D102
        if not self._timestamp_time:
            self._timestamp_time = datetime.datetime.now(
                tz=pytz.timezone(self.config["timestamp_timezone"])
            )

        return self._timestamp_time

    @property
    def filepath_replacement_map(self) -> Dict[str, str]:  # noqa: D102
        return {
            "stream_name": self.stream_name,
            "datestamp": self.timestamp_time.strftime(self.config["datestamp_format"]),
            "timestamp": self.timestamp_time.strftime(self.config["timestamp_format"]),
        }

    @property
    def destination_path(self) -> Path:  # noqa: D102
        result = self.config["file_naming_scheme"]
        for key, val in self.filepath_replacement_map.items():
            replacement_pattern = "{" f"{key}" "}"
            if replacement_pattern in result:
                result = result.replace(replacement_pattern, val)

        if self.config.get("output_path_prefix", None) is not None:
            result = f"{self.config['output_path_prefix']}{result}"

        return Path(result)

    def start_batch(self, context: dict) -> None:
        # Possible to get multiple batches, so be sure we don't create a new file & header each time
        self.logger.info("Processing start_batch()")
        if not self._wrote_header:
            self.logger.info("Writing header.")
            write_csv_header(self.destination_path, self.schema)
            self._wrote_header = True

    def process_batch(self, context: dict) -> None:
        records = context["records"]
        self.logger.info(f"Processing batch. Has {len(records)} records.")
        write_csv_rows(self.destination_path, records, self.schema)
