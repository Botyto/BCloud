from sqlalchemy import create_engine, Engine, String, BLOB
from sqlalchemy import select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session, object_session

from ..sql.columns import ensure_str_fit

from .base import Address, BlobIO, OpenMode, Blobs


class BlobModel(DeclarativeBase):
    pass


class Blob(BlobModel):
    __tablename__ = "_DataBlob"

    address: Mapped[str] = mapped_column(String(3072//4), primary_key=True)
    data: Mapped[bytes] = mapped_column(BLOB, nullable=True, default=None)


def addr_to_id(address: Address) -> str:
    id = str(address)
    ensure_str_fit("address", id, Blob.address)
    return id


class SqlBlobIO(BlobIO):
    blob: Blob
    cursor: int

    def __init__(self, blob: Blob, manager: Blobs, address: Address, mode: OpenMode):
        super().__init__(manager, address, mode)
        self.blob = blob
        self.cursor = 0

    @property
    def session(self):
        session = object_session(self.blob)
        assert session, "Blob is not attached to a session"
        return session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    def close(self):
        pass
    
    def flush(self):
        self.session.commit()

    def read(self, n: int = -1) -> bytes:
        if n == -1:
            return self.blob.data[self.cursor:]
        else:
            return self.blob.data[self.cursor:self.cursor+n]

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self.cursor = offset
        elif whence == 1:
            self.cursor += offset
        elif whence == 2:
            self.cursor = len(self.blob.data) + offset
        else:
            raise ValueError("Invalid whence value")
        return self.cursor

    def tell(self) -> int:
        return self.cursor

    def write(self, data: bytes|bytearray) -> int:
        self.blob.data = self.blob.data[:self.cursor] + data + self.blob.data[self.cursor+len(data):]
        self.cursor += len(data)
        return len(data)


class SqlBlobs(Blobs):
    engine: Engine
    session: Session

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string, pool_recycle=1800)
        BlobModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def exists(self, address: Address):
        statement = select(Blob).where(Blob.address == addr_to_id(address))
        return self.session.execute(statement).one_or_none() is not None

    def delete(self, address: Address):
        statement = delete(Blob).where(Blob.address == addr_to_id(address))
        self.session.execute(statement)
        self.session.commit()

    def open(self, address: Address, mode: OpenMode):
        statement = select(Blob).where(Blob.address == addr_to_id(address))
        blob = self.session.scalars(statement).one()
        return SqlBlobIO(blob, self, address, mode)

    def copy(self, src: Address, dst: Address):
        src_statement = select(Blob).where(Blob.address == addr_to_id(src))
        src_blob = self.session.scalars(src_statement).one()
        dst_statement = select(Blob).where(Blob.address == addr_to_id(dst))
        dst_blob = self.session.scalars(dst_statement).first()
        if dst_blob is not None:
            raise FileExistsError(dst)
        dst_blob = Blob(address=addr_to_id(dst), data=src_blob.data)
        self.session.add(dst_blob)
        self.session.commit()

    def rename(self, src: Address, dst: Address):
        src_statement = select(Blob).where(Blob.address == addr_to_id(src))
        src_blob = self.session.scalars(src_statement).first()
        if src_blob is None:
            raise FileNotFoundError()
        dst_statement = select(Blob).where(Blob.address == addr_to_id(dst))
        dst_blob = self.session.scalars(dst_statement).one_or_none()
        if dst_blob is not None:
            raise FileExistsError(dst)
        dst_blob = Blob(address=addr_to_id(dst), data=src_blob.data)
        self.session.delete(src_blob)
        self.session.add(dst_blob)
        self.session.commit()
