from enum import Enum


class MemoryType(str, Enum):
    INTEREST = "interest"
    PROJECT = "project"
    QUESTION = "question"
    NOTE = "note"
    SOURCE = "source"
    PAPER = "paper"
    CONCEPT = "concept"
    METHOD = "method"
    DATASET = "dataset"
    CODE = "code"
    DECISION = "decision"
    INSIGHT = "insight"
    FEEDBACK = "feedback"
