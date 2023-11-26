def default_palette() -> list[str]:
    palette = []

    i = 0

    while i < 25:
        palette.append("transparent")
        i = i + 1

    return palette

class SycartResponse():
    data: dict = {
        "error": True,
        "data": "Unknown error!"
    }

    def set_data(self, data):
        self.data["data"] = data

    def set_error(self, error):
        self.data["error"] = error