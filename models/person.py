class Person:
    
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError(f"Invalid email address: {value}")
        self._email = value.strip().lower()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name!r}, email={self._email!r})"
