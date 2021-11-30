from pydantic import BaseModel, Field, root_validator
from pydantic.dataclasses import dataclass


# pylint: disable=too-many-ancestors
class Tag(BaseModel):
    """Generic tag class

    Parameters
    ----------
    key : str
        Tag name

    value : str
        Tag value

    Attributes
    ----------
    key : str
        Tag name

    value : str
        Tag value

    Examples
    --------
    .. code:: python

        tag = Tag("some.tag", "some.val")
    """

    key: str
    value: str = str()

    class Config:
        frozen = True

    def __str__(self):
        return self.key

    @root_validator(pre=True)
    def to_dict(cls, values: dict) -> dict:
        """Bring to a single format."""
        if isinstance(values, dict) and ("key" not in values and "value" not in values):
            result = {}
            for key, val in values.items():
                result["key"] = key
                result["value"] = val

            return result

        return values
