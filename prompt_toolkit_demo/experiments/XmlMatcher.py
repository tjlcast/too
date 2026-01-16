from typing import List, Dict, Any, Callable, TypeVar, Generic, Optional, Union

T = TypeVar('T')
R = TypeVar('R')

XmlMatcherResult = Dict[str, Union[bool, str]]

class XmlMatcher(Generic[R]):
    def __init__(self, tag_name: str, transform: Optional[Callable[[XmlMatcherResult], R]]=None, position: int = 0):
        self.tag_name = tag_name
        self.transform = transform
        self.position = position
        self.index = 0
        self.chunks: List[XmlMatcherResult] = []
        self.cached: List[str] = []
        self.matched: bool = False
        self.state: str = "TEXT"  # "TEXT" | "TAG_OPEN" | "TAG_CLOSE"
        self.depth = 0
        self.pointer = 0

    def collect(self):
        if not self.cached:
            return

        last_chunk = self.chunks[-1] if self.chunks else None
        data = "".join(self.cached)
        matched = self.matched

        if last_chunk and last_chunk["matched"] == matched:
            last_chunk["data"] += data  # type: ignore
        else:
            self.chunks.append({
                "data": data,
                "matched": matched
            })

        self.cached = []

    def pop(self) -> List[Union[XmlMatcherResult, R]]:
        chunks = self.chunks
        self.chunks = []
        
        if not self.transform:
            return chunks  # type: ignore
        
        return [self.transform(chunk) for chunk in chunks]

    def _update(self, chunk: str):
        for char in chunk:
            self.cached.append(char)
            self.pointer += 1

            if self.state == "TEXT":
                if char == "<" and (self.pointer <= self.position + 1 or self.matched):
                    self.state = "TAG_OPEN"
                    self.index = 0
                else:
                    self.collect()
            elif self.state == "TAG_OPEN":
                if char == ">" and self.index == len(self.tag_name):
                    self.state = "TEXT"
                    if not self.matched:
                        self.cached = []
                    self.depth += 1
                    self.matched = True
                elif self.index == 0 and char == "/":
                    self.state = "TAG_CLOSE"
                elif char == " " and (self.index == 0 or self.index == len(self.tag_name)):
                    continue
                elif self.index < len(self.tag_name) and self.tag_name[self.index] == char:
                    self.index += 1
                else:
                    self.state = "TEXT"
                    self.collect()
            elif self.state == "TAG_CLOSE":
                if char == ">" and self.index == len(self.tag_name):
                    self.state = "TEXT"
                    self.depth -= 1
                    self.matched = self.depth > 0
                    if not self.matched:
                        self.cached = []
                elif char == " " and (self.index == 0 or self.index == len(self.tag_name)):
                    continue
                elif self.index < len(self.tag_name) and self.tag_name[self.index] == char:
                    self.index += 1
                else:
                    self.state = "TEXT"
                    self.collect()

    def final(self, chunk: Optional[str] = None) -> List[Union[XmlMatcherResult, R]]:
        if chunk:
            self._update(chunk)
        self.collect()
        return self.pop()

    def update(self, chunk: str) -> List[Union[XmlMatcherResult, R]]:
        self._update(chunk)
        return self.pop()