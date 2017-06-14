try:
    from itertools import filterfalse as ifilterfalse
    from cStringIO import StringIO
except ImportError:
    from itertools import ifilterfalse
    from io import StringIO
import re
from rtkit import comment


class RTParser(object):
    """ RFC5322 Parser - see https://tools.ietf.org/html/rfc5322"""

    HEADER = re.compile(r'^RT/(?P<v>.+)\s+(?P<s>(?P<i>\d+).+)')
    COMMENT = re.compile(r'^#\s+.+$')
    SYNTAX_COMMENT = re.compile(r'^>>\s+.+$')
    SECTION = re.compile(r'^--', re.M | re.U)

    @classmethod
    def parse(cls, body, decoder):
        """ :returns: A list of RFC5322-like section

        .. doctest::

            >>> decode = RTParser.decode
            >>> body = '''
            ...
            ... # c1
            ... spam: 1
            ... ham: 2,
            ...     3
            ... eggs:'''
            >>> RTParser.parse(body, decode)
            [[('spam', '1'), ('ham', '2,\\n3'), ('eggs', '')]]
            >>> RTParser.parse('# spam 1 does not exist.', decode)
            Traceback (most recent call last):
            ...
            RTNotFoundError: spam 1 does not exist
            >>> RTParser.parse('# Spam 1 created.', decode)
            [[('id', 'spam/1')]]
            >>> RTParser.parse('No matching results.', decode)
            []
            >>> decode = RTParser.decode_comment
            >>> RTParser.parse('# spam: 1\\n# ham: 2', decode)
            [[('spam', '1'), ('ham', '2')]]
        """
        section = cls.build(body)
        if len(section) == 1:
            try:
                comment.check(section[0])
            except (comment.RTNoMatch, IndexError):
                section = ''
            except comment.RTCreated as e:
                section = [['id: {0}'.format(e.id)]]
        return [decoder(lines) for lines in section]

    @classmethod
    def decode(cls, lines):
        """:return: A list of 2-tuples parsing 'k: v' and skipping comments

        .. doctest::

            >>> RTParser.decode(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
            [('spam', '1'), ('ham', '2, 3'), ('eggs', '')]
            >>> RTParser.decode(['<!DOCTYPE HTML PUBLIC >', '<html><head>',])
            []
        """
        try:
            lines = ifilterfalse(cls.COMMENT.match, lines)
            return [(k.encode('utf-8'), v.strip(' ').encode('utf-8')) for k, v in [l.split(':', 1) for l in lines]]
        except (ValueError, IndexError):
            return []

    @classmethod
    def decode_comment(cls, lines):
        """:return: A list of 2-tuples parsing '# k: v'

        .. doctest::

            >>> RTParser.decode_comment(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
            [('c1', 'c2')]
            >>> RTParser.decode_comment(['# Syntax error.', '>> c1: c2', 'ham: 2, 3', 'eggs:'])
            [('c1', 'c2')]
        """
        flines = filter(cls.COMMENT.match, lines)
        if len(flines) == 1 and flines[0] == '# Syntax error.':
            flines = [l.strip('>> ') for l in filter(cls.SYNTAX_COMMENT.match, lines)]
        return [(k.strip('# ').encode('utf-8'), v.strip(' ').encode('utf-8')) for k, v in [l.split(':', 1) for l in flines]]

    @classmethod
    def build(cls, body):
        """Build logical lines from a RFC5322-like string

        :returns: A list of strings
        .. doctest::

            >>> body = '''RT/1.2.3 200 Ok
            ...
            ... # a
            ...   b
            ... spam: 1
            ...
            ... ham: 2,
            ...     3
            ... --
            ... # c
            ... spam: 4
            ... ham:
            ... --
            ... a -- b
            ... '''
            >>> RTParser.build(body)
            [[u'# a\\nb', u'spam: 1', u'ham: 2,\\n3'], [u'# c', u'spam: 4', u'ham:'], [u'a -- b']]
        """
        def build_section(section):
            logic_lines = []
            for line in StringIO(section):
                # strip trailing newline
                if line and line[-1] == '\n':
                    line = line.rstrip('\n')
                if not line or cls.HEADER.match(line):
                    continue
                if line[0].isspace():
                    logic_lines[-1] += '\n' + line.strip(' ')
                else:
                    logic_lines.append(line)
            return logic_lines
        return [build_section(b) for b in cls.SECTION.split(body.decode('utf-8', 'ignore'))]
