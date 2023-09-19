from sqlalchemy.orm import Query
import typing


ItemType = typing.TypeVar("ItemType")


class PaginationResult(typing.Generic[ItemType]):
	"""Result of a pagination query."""
	total: int
	page: int
	page_size: int
	items: typing.Iterable[ItemType]

	@property
	def max_page(self) -> int:
		return self.total // self.page_size + (self.total % self.page_size > 0)
	
	@property
	def has_previous(self) -> bool:
		return self.page > 0

	@property
	def has_next(self) -> bool:
		return self.page < self.max_page - 1

	def __init__(self, total: int, page: int, page_size: int, items: typing.Iterable[ItemType]):
		self.total = total
		self.page = page
		self.page_size = page_size
		self.items = items


class PaginationInput:
	"""Input for a pagination query."""
	DEFAULT_PAGE_SIZE = 20

	sort: typing.List[str]|None
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

	def of(self, query: Query, filter: typing.Callable[[ItemType], ItemType]|None = None) -> PaginationResult[ItemType]:
		assert len(query.column_descriptions) == 1, "Query must return a single column"
		self.validate()
		total = query.count()
		if self.sort:
			clauses = []
			column_type = query.column_descriptions[0]["type"]
			for key in self.sort:
				if key.startswith("-"):
					clause = getattr(column_type, key[1:]).desc()
				elif key.startswith("+"):
					clause = getattr(column_type, key[1:]).asc()
				else:
					clause = getattr(column_type, key).asc()
				clauses.append(clause)
			query = query.order_by(*clauses)
		items = query \
			.offset(self.offset) \
			.limit(self.real_size) \
			.all()
		if filter is not None:
			items = [filter(item) for item in items]
			items = [item for item in items if item is not None]
		return PaginationResult(total, self.real_page, self.real_size, items)
