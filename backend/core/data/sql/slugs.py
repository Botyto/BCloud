import re
import sqlalchemy
from sqlalchemy import Column, String
import sqlalchemy.event
from sqlalchemy.orm import class_mapper, Session, InstrumentedAttribute
from sqlalchemy.orm.state import InstanceState
from typing import Dict, List, Type, TYPE_CHECKING
from uuid import uuid4
import unidecode

if TYPE_CHECKING:
    from .database import Model

SLUG_BASE_MAX_LENGTH = 32
SLUG_SUFFIX_LENGTH = 8
SLUG_LENGTH = SLUG_BASE_MAX_LENGTH + SLUG_SUFFIX_LENGTH + 1

def slug_info(*origins: str|InstrumentedAttribute[String], once: bool = False, **kwargs):
    return {
        "slug": True,
        "origins": origins,
        "once": once,
        **kwargs,
    }


class SlugInfo:
    key: str
    origins: List[str]|None
    generate_once: bool

    def __init__(self, key: str, origins: List[str]|None, generate_once: bool):
        self.key = key
        self.origins = origins if origins else None
        self.generate_once = generate_once

NO_SLUG = SlugInfo("", None, False)

TYPE_TO_SLUG_INFO: Dict[Type["Model"], SlugInfo] = {}
def find_slug_info(entity_type: Type["Model"]) -> SlugInfo:
    slug_info = TYPE_TO_SLUG_INFO.get(entity_type, None)
    if slug_info is None:
        column_attrs = class_mapper(entity_type).column_attrs
        for column_attr in column_attrs:
            attr: InstrumentedAttribute = getattr(entity_type, column_attr.key)
            attr_info = attr.info
            if attr_info is not None and "slug" in attr_info:
                if slug_info is not None:
                    raise TypeError(f"Multiple slugs for `{entity_type}`")
                origins = attr_info["origins"]
                once = attr_info.get("once", False)
                slug_info = SlugInfo(column_attr.key, origins, once)
        slug_info = slug_info or NO_SLUG
        TYPE_TO_SLUG_INFO[entity_type] = slug_info
    return slug_info

SLUG_ORIGIN_COLUMNS = ["name", "title", "display_name"]
TYPE_TO_ORIGIN_NAMES: Dict[Type["Model"], List[str]] = {}
def find_origin_names(entity_type: Type["Model"], slug_info: SlugInfo) -> List[str]:
    origin_names = TYPE_TO_ORIGIN_NAMES.get(entity_type)
    if origin_names is None:
        if not slug_info.origins:
            for member_name in SLUG_ORIGIN_COLUMNS:
                if hasattr(entity_type, member_name):
                    origin_names = [member_name]
                    break
        else:
            origin_names = slug_info.origins
        if not origin_names:
            raise TypeError(f"No origin columns for `{entity_type}`")
        TYPE_TO_ORIGIN_NAMES[entity_type] = origin_names
    return origin_names

FORBIDDEN_PATTERN = re.compile(r"[^A-Za-z0-9-]+")
CONSECUTIVE_DASH = re.compile(r"-+")
def slugify(s: str) -> str:
    slug = s.lower()
    slug = unidecode.unidecode(slug)
    slug = FORBIDDEN_PATTERN.sub("-", slug)
    slug = CONSECUTIVE_DASH.sub("-", slug)
    slug = slug.strip("-")
    return slug.lower().replace(" ", "-")

def generate_slug(entity: "Model", slug_info: SlugInfo, origins: List[str]) -> str:
    if not origins:
        return ""
    slug = "-".join(slugify(o) for o in origins)
    if len(slug) > SLUG_BASE_MAX_LENGTH:
        slug = slug[:SLUG_BASE_MAX_LENGTH]
    suffix = str(uuid4())
    suffix = suffix[:suffix.index("-")]
    assert len(suffix) == SLUG_SUFFIX_LENGTH
    slug = f"{slug}-{suffix}"
    assert len(slug) <= SLUG_LENGTH
    # TODO check if slug is unique (and generate a new suffix if needed)
    return slug

@sqlalchemy.event.listens_for(Session, "before_flush")
def on_before_flush(session: Session, flush_context, instances):
    def process_slugs(entities):
        for entity in entities:
            slug_info = find_slug_info(type(entity))
            if slug_info is NO_SLUG:
                continue
            if slug_info.generate_once and getattr(entity, slug_info.key):
                continue
            origin_names = find_origin_names(type(entity), slug_info)
            entity_inspect: InstanceState = sqlalchemy.inspect(entity)
            inspect_attrs = entity_inspect.attrs
            if any(inspect_attrs[oname].history.has_changes() for oname in origin_names):
                origins = [getattr(entity, o) for o in origin_names]
                new_slug = generate_slug(entity, slug_info, origins)
                setattr(entity, slug_info.key, new_slug)
    process_slugs(session.new)
    process_slugs(session.dirty)

def ensure_slug_setup(cls):
    cls_name = cls.__name__
    columns: List[Column] = cls.__table__.columns
    for column in columns:
        if not isinstance(column.type, String):
            continue
        if column.info is None or "slug" not in column.info:
            continue
        assert (column.type.length or 0) == SLUG_LENGTH, f"Slug column {cls_name}.{column.name} must have a length of `SLUG_LENGTH` ({SLUG_LENGTH}) specified"
