from frontend.vertex import MainVertex


class SelectionList:
    SELECTED = None

    def __init__(self):
        self.SELECTED = []
        self.index = 0

    def __next__(self):
        if self.index < len(self.SELECTED):
            index = self.index
            self.index += 1
            return self.SELECTED[index]
        raise StopIteration()

    def __iter__(self):
        return self

    def __getitem__(self, index):
        return self.SELECTED[index]

    def length(self):
        return len(self.SELECTED)

    def append(self, item):
        self.SELECTED.append(item)

        if isinstance(item, MainVertex):
            item.highlight_self()
            item.setPersistent(True)

    def remove(self, item):
        self.SELECTED.remove(item)

        if isinstance(item, MainVertex):
            item.unhighlight_self()
            item.setPersistent(False)

    def contains(self, item):
        return item in self.SELECTED

    def clear(self):
        for item in self.SELECTED:
            if isinstance(item, MainVertex) and not item.isHighlighted():
                item.unhighlight_self()
                item.setPersistent(False)

        self.SELECTED.clear()
        self.index = 0

    def is_empty(self):
        return self.SELECTED == []
