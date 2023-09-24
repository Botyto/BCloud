from sqlalchemy.orm import Session
from sqlalchemy.sql import Select, text as sql_text
from typing import Callable, Iterable, Generic, List, Tuple, TypeVar


ItemType = TypeVar("ItemType")


class PagesResult(Generic[ItemType]):
	"""Result of a pagination query."""
	total: int
	page: int
	page_size: int
	items: Iterable[ItemType]

	@classmethod
	def empty(cls) -> "PagesResult[ItemType]":
		return cls(0, 0, 0, [])

	@property
	def max_page(self) -> int:
		return self.total // self.page_size
	
	@property
	def has_previous(self) -> bool:
		return self.page > 0

	@property
	def has_next(self) -> bool:
		return self.page < self.max_page - 1

	def __init__(self, total: int, page: int, page_size: int, items: Iterable[ItemType]):
		self.total = total
		self.page = page
		self.page_size = page_size
		self.items = items


class PagesInput:
	"""Input for a pagination query."""
	DEFAULT_PAGE_SIZE = 20

	sort: List[str]|None
	page: int|None
	page_size: int|None

	def validate(self):
		if self.real_page < 0:
			raise ValueError("Page must be positive")
		if self.real_size <= 0:
			raise ValueError("Page size must be positive")

	@property
	def real_page(self) -> int:
		return self.page or 0

	@property
	def real_size(self) -> int:
		return self.page_size or self.DEFAULT_PAGE_SIZE

	@property
	def offset(self) -> int:
		return self.real_page * self.real_size

	def of(self, session: Session, statement: Select[Tuple[ItemType]], filter: Callable[[ItemType], bool]|None = None) -> PagesResult[ItemType]:
		assert len(statement.column_descriptions) == 1, "Query must return a single column"
		self.validate()
		column_type = statement.column_descriptions[0]["type"]
		count_statement = statement.with_only_columns(sql_text("count(*)"))
		total = session.execute(count_statement).scalar() or 0
		if self.sort:
			clauses = []
			for key in self.sort:
				if key.startswith("-"):
					clause = getattr(column_type, key[1:]).desc()
				elif key.startswith("+"):
					clause = getattr(column_type, key[1:]).asc()
				else:
					clause = getattr(column_type, key).asc()
				clauses.append(clause)
			statement = statement.order_by(*clauses)
		statement = statement.offset(self.offset).limit(self.real_size)
		items = session.scalars(statement).all()
		if filter is not None:
			items = [item for item in items if filter(item)]
			items = [item for item in items if item is not None]
		return PagesResult(total, self.real_page, self.real_size, items)
