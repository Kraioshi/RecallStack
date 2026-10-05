from uuid import UUID

from app.core.enums.question import QuestionDifficulty

type DifficultyCounts = dict[QuestionDifficulty, int]
type TopicDifficultyCounts = dict[UUID, DifficultyCounts]
