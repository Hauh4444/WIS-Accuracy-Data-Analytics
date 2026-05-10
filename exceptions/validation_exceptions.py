class ValidationError(Exception):
    pass


class InvalidHoursError(ValidationError):
    pass


class MissingEmployeeDataError(ValidationError):
    pass