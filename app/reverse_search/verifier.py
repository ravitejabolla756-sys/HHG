from .parser import Candidate

def select_match(candidates: list[Candidate]) -> Candidate:
    if not candidates:
        raise RuntimeError("Reverse-image search returned no public social-media URL; refusing to invent a match")
    return candidates[0]
