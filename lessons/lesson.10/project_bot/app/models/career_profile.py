from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CareerProfile:
    user_id: int
    profession: str
    grade: str

    def to_message(self) -> str:
        text = f"""
        Спасибо! Я записал твою анкету.
        Твоя профессия - {self.profession}
        Твоя уровень - {self.grade}
        """
        return text

    def to_dict(self) -> dict[str, int | str]:
        prof_dict = {
            'user_id': self.user_id,
            'profession': self.profession,
            'grade': self.grade,
        }
        return prof_dict