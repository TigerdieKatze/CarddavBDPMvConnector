from typing import List

class UserDto:
    def __init__(self, firstname: str, lastname: str, own_email: str, secondary_email: str, parent_email: str, groups: List[str]):
        self.firstname = firstname
        self.lastname = lastname
        self.own_email = own_email
        self.secondary_email = secondary_email
        self.parent_email = parent_email
        self.groups = groups

    @property
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"