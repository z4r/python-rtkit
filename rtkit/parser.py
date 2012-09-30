from itertools import ifilterfalse
import re
from rtkit import comment


class RTParser(object):
    HEADER = re.compile(r'^RT/(?P<v>.+)\s+(?P<s>(?P<i>\d+).+)')
    COMMENT = re.compile(r'^#\s+.+$')
    SECTION = re.compile(r'^--', re.M | re.U)

    @classmethod
    def parse(cls, body, decoder):
        r""" Return a list of RFC5322-like section
        >>> decode = RTParser.decode
        >>> body = '''
        ...
        ... # c1
        ... spam: 1
        ... ham: 2,
        ...     3
        ... eggs:'''
        >>> RTParser.parse(body, decode)
        [[('spam', '1'), ('ham', '2, 3'), ('eggs', '')]]
        >>> RTParser.parse('# spam 1 does not exist.', decode)
        Traceback (most recent call last):
            ...
        RTNotFoundError: spam 1 does not exist
        >>> RTParser.parse('# Spam 1 created.', decode)
        [[('id', 'spam/1')]]
        >>> RTParser.parse('No matching results.', decode)
        []
        >>> decode = RTParser.decode_comment
        >>> RTParser.parse('# spam: 1\n# ham: 2', decode)
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
        """ Return a list of 2-tuples parsing 'k: v' and skipping comments
        >>> RTParser.decode(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('spam', '1'), ('ham', '2, 3'), ('eggs', '')]
        >>> RTParser.decode(['<!DOCTYPE HTML PUBLIC >', '<html><head>',])
        []
        """
        try:
            lines = ifilterfalse(cls.COMMENT.match, lines)
            return [(k, v.strip(' ')) for k, v in [l.split(':', 1) for l in lines]]
        except ValueError, IndexError:
            return []

    @classmethod
    def decode_comment(cls, lines):
        """ Return a list of 2-tuples parsing '# k: v'
        >>> RTParser.decode_comment(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('c1', 'c2')]
        >>>
        """
        lines = filter(cls.COMMENT.match, lines)
        return [(k.strip('# '), v.strip(' ')) for k, v in [l.split(':', 1) for l in lines]]

    @classmethod
    def build(cls, body):
        """ Build logical lines from a RFC5322-like string
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
        [['# a b', 'spam: 1', 'ham: 2, 3'], ['# c', 'spam: 4', 'ham:'], ['a -- b']]
        """
        def build_section(section):
            logic_lines = []
            for line in filter(None, section.splitlines()):
                if cls.HEADER.match(line):
                    continue
                if line[0].isspace():
                    logic_lines[-1] += ' ' + line.strip(' ')
                else:
                    logic_lines.append(line)
            return logic_lines
        return [build_section(b) for b in cls.SECTION.split(body)]
