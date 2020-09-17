from spmclient import consts


class DisplayFormat:
    """Reference data format"""

    def __init__(self, subject: str = consts.SUBJECT_REF, side: str = consts.side[0]):
        self.side = side
        self.subject = subject

    def color(self) -> str:
        if self.subject == consts.SUBJECT_REF:
            return 'k'
        elif self.side == consts.SIDE_LEFT:
            return 'r'
        elif self.side == consts.SIDE_RIGHT:
            return 'b'
        else:
            raise RuntimeError(f"Can't find color for subject={self.subject} and side={self.side}.")

    def line(self) -> str:
        if self.subject == consts.SUBJECT_AFTER:
            return '--'
        else:
            return '-'

    def marks(self) -> str:
        return ''

    def line_and_marks(self) -> str:
        return self.marks() + self.line()

    def line_index(self):
        if self.subject == consts.SUBJECT_REF:
            return 0
        if self.subject == consts.SUBJECT_B4:
            return 1
        if self.subject == consts.SUBJECT_AFTER:
            return 2
