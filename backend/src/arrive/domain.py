from enum import Enum


class StringEnum(str, Enum):
    pass


class Privacy(StringEnum):
    PRIVATE = "private"
    ANONYMIZED = "anonymized"
    SHAREABLE = "shareable"


class MaterialKind(StringEnum):
    THOUGHT = "thought"
    FEELING = "feeling"
    EXPERIENCE = "experience"
    CONTRADICTION = "contradiction"
    QUESTION = "question"
    QUOTE = "quote"
    CONTEXT = "context"


class SourceKind(StringEnum):
    WEB_ARTICLE = "web_article"
    BOOK = "book"
    VIDEO = "video"
    PODCAST = "podcast"
    SPEECH = "speech"
    CONVERSATION = "conversation"
    OTHER = "other"


class SourceStance(StringEnum):
    PENDING = "pending"
    ENDORSED = "endorsed"
    PARTIALLY_ENDORSED = "partially_endorsed"
    REFERENCE = "reference"
    QUESTIONED = "questioned"
    OPPOSED = "opposed"


class ContentStatus(StringEnum):
    REGISTERED = "registered"
    METADATA_ONLY = "metadata_only"
    SUMMARIZED = "summarized"
    MAPPED = "mapped"
    CITED = "cited"
    UNAVAILABLE = "unavailable"


class Rights(StringEnum):
    THIRD_PARTY_COPYRIGHT = "third_party_copyright"
    LICENSED = "licensed"
    PUBLIC_DOMAIN = "public_domain"
    USER_OWNED = "user_owned"
    UNKNOWN = "unknown"


class PropositionAttribution(StringEnum):
    AUTHOR_EXPLICIT = "author_explicit"
    COLLABORATOR_SUMMARY = "collaborator_summary"


class Resonance(StringEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"
    UNSPECIFIED = "unspecified"


class Agreement(StringEnum):
    AGREE = "agree"
    MOSTLY_AGREE = "mostly_agree"
    PARTLY_AGREE = "partly_agree"
    UNCERTAIN = "uncertain"
    DISAGREE = "disagree"
    UNSPECIFIED = "unspecified"


class Adoption(StringEnum):
    ADOPT = "adopt"
    ADAPT = "adapt"
    CITE = "cite"
    NOT_USE = "not_use"
    UNDECIDED = "undecided"


class Confidence(StringEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimePrecision(StringEnum):
    MINUTE = "minute"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    UNKNOWN = "unknown"


class ThoughtNodeType(StringEnum):
    MATERIAL = "material"
    PROPOSITION = "proposition"
    QUESTION = "question"
    CONCEPT = "concept"
    UNKNOWN = "unknown"
    BOUNDARY = "boundary"


class ThoughtRelation(StringEnum):
    SUPPORTS = "supports"
    CHALLENGES = "challenges"
    CAUSES = "causes"
    QUALIFIES = "qualifies"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    RELATES_TO = "relates_to"
