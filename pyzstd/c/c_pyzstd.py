from collections import namedtuple
from enum import IntEnum

from ._zstd import *
from . import _zstd

__all__ = (# From this file
           'compressionLevel_values', 'get_frame_info',
           'CParameter', 'DParameter', 'Strategy',
           # From _zstd
           'ZstdCompressor', 'RichMemZstdCompressor',
           'ZstdDecompressor', 'EndlessZstdDecompressor',
           'ZstdDict', 'ZstdError', 'decompress', 'get_frame_size',
           'compress_stream', 'decompress_stream',
           'zstd_version', 'zstd_version_info', 'zstd_support_multithread')


# Used in __init__.py
_ZSTD_DStreamInSize = _zstd._ZSTD_DStreamInSize
_train_dict = _zstd._train_dict
_finalize_dict = _zstd._finalize_dict


# compressionLevel_values
_nt_values = namedtuple('values', ['default', 'min', 'max'])
compressionLevel_values = _nt_values(_zstd._ZSTD_defaultCLevel,
                                     _zstd._ZSTD_minCLevel,
                                     _zstd._ZSTD_maxCLevel)


_nt_frame_info = namedtuple('frame_info',
                            ['decompressed_size', 'dictionary_id'])

def get_frame_info(frame_buffer):
    """Get zstd frame infomation from a frame header.

    Parameter
    frame_buffer: A bytes-like object. It should starts from the beginning of
                  a frame, and needs to include at least the frame header (6 to
                  18 bytes).

    Return a two-items namedtuple: (decompressed_size, dictionary_id)

    If decompressed_size is None, decompressed size is unknown.

    dictionary_id is a 32-bit unsigned integer value. 0 means dictionary ID was
    not recorded in the frame header, the frame may or may not need a dictionary
    to be decoded, and the ID of such a dictionary is not specified.

    It's possible to append more items to the namedtuple in the future."""

    ret_tuple = _zstd._get_frame_info(frame_buffer)
    return _nt_frame_info(*ret_tuple)


class CParameter(IntEnum):
    """Compression parameters"""

    compressionLevel           = _zstd._ZSTD_c_compressionLevel
    windowLog                  = _zstd._ZSTD_c_windowLog
    hashLog                    = _zstd._ZSTD_c_hashLog
    chainLog                   = _zstd._ZSTD_c_chainLog
    searchLog                  = _zstd._ZSTD_c_searchLog
    minMatch                   = _zstd._ZSTD_c_minMatch
    targetLength               = _zstd._ZSTD_c_targetLength
    strategy                   = _zstd._ZSTD_c_strategy

    enableLongDistanceMatching = _zstd._ZSTD_c_enableLongDistanceMatching
    ldmHashLog                 = _zstd._ZSTD_c_ldmHashLog
    ldmMinMatch                = _zstd._ZSTD_c_ldmMinMatch
    ldmBucketSizeLog           = _zstd._ZSTD_c_ldmBucketSizeLog
    ldmHashRateLog             = _zstd._ZSTD_c_ldmHashRateLog

    contentSizeFlag            = _zstd._ZSTD_c_contentSizeFlag
    checksumFlag               = _zstd._ZSTD_c_checksumFlag
    dictIDFlag                 = _zstd._ZSTD_c_dictIDFlag

    nbWorkers                  = _zstd._ZSTD_c_nbWorkers
    jobSize                    = _zstd._ZSTD_c_jobSize
    overlapLog                 = _zstd._ZSTD_c_overlapLog

    def bounds(self):
        """Return lower and upper bounds of a compression parameter, both inclusive."""
        # 1 means compression parameter
        return _zstd._get_param_bounds(1, self.value)


class DParameter(IntEnum):
    """Decompression parameters"""

    windowLogMax = _zstd._ZSTD_d_windowLogMax

    def bounds(self):
        """Return lower and upper bounds of a decompression parameter, both inclusive."""
        # 0 means decompression parameter
        return _zstd._get_param_bounds(0, self.value)


class Strategy(IntEnum):
    """Compression strategies, listed from fastest to strongest.

    Note : new strategies _might_ be added in the future, only the order
    (from fast to strong) is guaranteed.
    """
    fast     = _zstd._ZSTD_fast
    dfast    = _zstd._ZSTD_dfast
    greedy   = _zstd._ZSTD_greedy
    lazy     = _zstd._ZSTD_lazy
    lazy2    = _zstd._ZSTD_lazy2
    btlazy2  = _zstd._ZSTD_btlazy2
    btopt    = _zstd._ZSTD_btopt
    btultra  = _zstd._ZSTD_btultra
    btultra2 = _zstd._ZSTD_btultra2


# Set CParameter/DParameter types for validity check
_zstd._set_parameter_types(CParameter, DParameter)