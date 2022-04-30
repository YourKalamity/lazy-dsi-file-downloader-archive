import zipfile

from . import deflate64
from ._patcher import patch

# Since none of the public API of zipfile needs to be patched, we don't have to worry about
# ensuring that this is prior to other code importing things from zipfile.

# This is already defined in zipfile.compressor_names, for error-handling purposes
zipfile.ZIP_DEFLATED64 = 9  # type: ignore[attr-defined]


@patch(zipfile, '_check_compression')
def deflate64_check_compression(compression: int) -> None:
    if compression == zipfile.ZIP_DEFLATED64:  # type: ignore[attr-defined]
        pass
    else:
        patch.originals['_check_compression'](compression)


@patch(zipfile, '_get_decompressor')
def deflate64_get_decompressor(compress_type: int):
    if compress_type == zipfile.ZIP_DEFLATED64:  # type: ignore[attr-defined]
        return deflate64.Deflate64()
    else:
        return patch.originals['_get_decompressor'](compress_type)


@patch(zipfile.ZipExtFile, '__init__')
def deflate64_ZipExtFile_init(self, *args, **kwarg):  # noqa: N802
    patch.originals['__init__'](self, *args, **kwarg)
    if self._compress_type == zipfile.ZIP_DEFLATED64:
        self.MIN_READ_SIZE = 64 * 2 ** 10
