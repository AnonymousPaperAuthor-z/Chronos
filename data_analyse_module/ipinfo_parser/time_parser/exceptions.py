
# Abnormal LMT format exception class
class AbnormalLMTFormat(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# LMT string exception
class AbnoramlLMTString(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# Unmatched lmt string
class UnformatLMTString(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
