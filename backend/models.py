from typing import List

class UserDto:
    def __init__(self, firstname: str, lastname: str, own_email: str, secondary_email: str, parent_email: str, groups: List[str]):
        self.firstname = str(firstname)
        self.lastname = str(lastname)
        self.own_email = str(own_email)
        self.secondary_email = str(secondary_email) if secondary_email else None
        self.parent_email = str(parent_email) if parent_email else None
        self.groups = groups

    @property
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"