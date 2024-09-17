from dataclasses import dataclass


@dataclass
class Either:
    left_value: any = None
    right_value: any = None

    def is_right(self):
        return self.right_value is not None

    def is_left(self):
        return self.left_value is not None


def left(value):
    return Either(left_value=value)


def right(value):
    return Either(right_value=value)
