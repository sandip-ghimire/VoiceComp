import os

from django.utils.deprecation import MiddlewareMixin
from compressor.filters import CompilerFilter


class RangesMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 200 or not hasattr(response, 'file_to_stream'):
            return response
        http_range = request.META.get('HTTP_RANGE')
        if not (http_range and http_range.startswith('bytes=') and http_range.count('-') == 1):
            return response
        if_range = request.META.get('HTTP_IF_RANGE')
        if if_range and if_range != response.get('Last-Modified') and if_range != response.get('ETag'):
            return response
        f = response.file_to_stream
        statobj = os.fstat(f.fileno())
        start, end = http_range.split('=')[1].split('-')
        if not start:  # requesting the last N bytes
            start = max(0, statobj.st_size - int(end))
            end = ''
        start, end = int(start or 0), int(end or statobj.st_size - 1)
        assert 0 <= start < statobj.st_size, (start, statobj.st_size)
        end = min(end, statobj.st_size - 1)
        f.seek(start)
        old_read = f.read
        f.read = lambda n: old_read(min(n, end + 1 - f.tell()))
        response.status_code = 206
        response['Content-Length'] = end + 1 - start
        response['Content-Range'] = 'bytes %d-%d/%d' % (start, end, statobj.st_size)
        return response


class UglifyFilter(CompilerFilter, MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # do stuff with request

        response = self.get_response(request)
        return response

    def minifyJS(self, srcText):
        from slimit import minify
        return minify(srcText, mangle=True, mangle_toplevel=True)

    def doProcessFiles(self, minifyProc, sourcePaths, minPath):
        mf = None
        try:
            mf = open(minPath, 'w')

            for srcFile in sourcePaths:
                print(srcFile)
                with open(srcFile) as inputFile:
                    srcText = inputFile.read()
                    minText = minifyProc(srcText)
                mf.write(minText)
        finally:
            if mf and not mf.closed:
                mf.close()

    def doJSMin(self, sourcePaths, minPath):
        return self.doProcessFiles(self.minifyJS, sourcePaths, minPath)
