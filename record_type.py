from collections import OrderedDict
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class RecordType:
    ignore_record_types = set()
    record_limit = 10

    def __init__(self, record_type: str) -> None:
        self.record_type = record_type
        self.values = OrderedDict()

    @classmethod
    def should_ignore(cls, record_type: str) -> bool:
        if record_type in cls.ignore_record_types:
            return True
        if record_type.endswith("s"):
            cls.ignore_record_types.add(record_type)
            return True
        return False

    def __ignore_check(self):
        number_to_remove = max(len(self.values) - (self.record_limit - 1), 0)

        for _ in range(number_to_remove):
            self.values.popitem()

    def __additional_actions(self, value: str) -> Tuple[bool, str, Any]:

        match self.record_type:
            case "Contact":
                pass
            case "Invoice":
                pass
            case _:
                return (False, value, None)

    def add_value(self, value: str, value_to_store: Any = None) -> bool:
        """value: Add to values OrderedDict if new value. Otherwise, move to the end.\n
        value_to_store: Store pair for key value (Contact:Email Address)\n
        returns bool if the dictionary was updated."""
        self.__ignore_check()
        if value not in self.values:

            if self.__additional_actions(value):
                pass

            self.values[value] = value_to_store
            self.values.move_to_end(value, last=False)
            logger.debug(f"Added {value} to {self.record_type} dictionary.")
            return True

        if next(iter(self.values)) == value:
            return False
        else:
            self.values.move_to_end(value, last=False)
            logger.debug(
                f"{value} exists in {self.record_type}. Moved to front of dictionary."
            )
            return True


if __name__ == "__main__":
    a = RecordType("aa")
    b = RecordType("ab")
    l = [b, a]
    l.sort(key=lambda x: x.record_type)
    print([x.record_type for x in l])

    one = {"a": "b", "b": None}
    two = {"a": "c", "b": "b"}
    three = OrderedDict.fromkeys("ab")
    limit_test = RecordType("limit_test")
    for x in range(30):
        limit_test.add_value(x)
    print(limit_test.values)
    print(next(iter(limit_test.values)))
