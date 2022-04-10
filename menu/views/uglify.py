from compressor.conf import settings
from compressor.filters import CompilerFilter


class UglifyFilter(CompilerFilter):
    command = "{binary} {args}"
    options = (
        ("binary", settings.COMPRESS_UGLIFY_BINARY),
        ("args", settings.COMPRESS_UGLIFY_JS_ARGUMENTS),
    )
