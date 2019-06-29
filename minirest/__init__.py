sample = """

This is a title
---------------

This is a paragraph that
might have multiple lines *bold*.

This is a paragraph that introduce some code::

    for i in range(1):
        pass

New paragraph with only one line :a:`directive` and the rest of the paragraph, 
a second :d:`directive with many words`.

.. directive::
    :arg:
    :arg:

    body

The end
"""

def _leading_space(content):
    """
    count the number of leading spaces
    """
    n = 0
    for c in content:
        if c != ' ':
            return n
        else:
            n+=1
    return n

# TOKENS

class Token:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

class Colon(Token): match = ':' 
class Backtick(Token): match = '`'
class WhiteSpace(Token): match = ' '
class NL(Token): match = '\n'
class Text(Token): match = None


tmap = {}
for _class in Token.__subclasses__():
    if _class.match:
        tmap[_class.match] = _class

def get_token_type(str):
    return tmap.get(str, Text)(str)

class Node:
    def __init__(self, content):
        self.content = content
        self.indent = _leading_space(content)

class Page(Node):
    pass

class Paragraph(Node):
    pass
class InlineDirective(Node):

    def __init__(self, name,  content):
        super().__init__(content)
        self.name = name
    def __repr__(self):
        return f"InlineDirective({self.name} | {self.content})"

class Line(Node):

    def __repr__(self):
        return f"Line({repr(self.content)}, {self.indent})"

class Header(Node):

    def __init__(self, content):
        super().__init__(content)
        self.level = None

    def __repr__(self):
        return f"Header({repr(self.content)}, {self.indent})"

class Parser:

    def __init__(self):
        self.subs = []


    def parse(self, token_stream):

        pass

#class RawParser(Parser):
#    """
#    Yield all the inner token unchanged; this is the final leaf
#    """
#    
#    def close(self):
#        pass
#
#    def parse(self, token_stream):
#        for t in token_stream:
#            yield token

class TryNext(Exception):pass

class NoneParser(Parser):
    def parse(self, content):
        return content[0], content[1:]

class OrParser(Parser):

    def __init__(self, tries):
        self.tries = tries

    def parse(self, content):
        for t in self.tries:
            try:
                res = t.parse(content)
            except TryNext:
                continue
            else:
                return res
        raise TryNext

class RepeatParser(Parser):

    def __init__(self, parser):
        self.parser = parser

    def parse(self, content):
        res = []
        n = None
        while content:
            n_content = self.parser.parse(content)
            try:
                n, content = n_content
            except ValueError as e:
                raise ValueError(f"{n_content}") from e


            res.append(n)
        return res, content






class DefaultDirectiveParser(Parser):

    def parse(self, token_list):
        t1 = token_list[0]
        if not isinstance(t1, Backtick):
            raise TryNext


        name = 'Default'
        content = []
        i = 0
        for i,t in enumerate(token_list[1:]):
            if isinstance(t, Backtick):
                break
            if not isinstance(t, (Text, WhiteSpace)):
                raise TryNext(f"{t} is of Type {type(t)}")
            content.append(t)
        return InlineDirective(name, content), token_list[i+2:]


class NamedDirectiveParser(Parser):

    def parse(self, token_list):
        try:
            t1,t2,t3,t4 = token_list[:4]
        except ValueError:
            raise TryNext
        if not isinstance(t1, Colon):
            raise TryNext
        if not isinstance(t2, Text):
            raise TryNext
        if not isinstance(t3, Colon):
            raise TryNext
        if not isinstance(t4, Backtick):
            raise TryNext


        name = t2
        content = []
        for i,t in enumerate(token_list[4:]):
            if isinstance(t, Backtick):
                break
            if not isinstance(t, (Text, WhiteSpace)):
                raise TryNext(f"{t} is of Type {type(t)}")
            content.append(t)
        return InlineDirective(name, content), token_list[i+5:]


def tokenize(stream):
    current = ''
    split = ' \n:`'
    for c in stream:
        if c in split:
            if current:
                yield get_token_type(current)
            current = ''
            yield get_token_type(c)
        else:
            current = current + c
    if current:
        yield get_token_type(current)


def by_lines(tokens):
    """
    Group tokens by lines; this will be useful to detect things like titles; and indented blocks.
    """
    line = []
    for token in tokens:
        if token == '\n':
            yield Line(line)
            line = []
        else:
            line.append(token)
    if line:
        yield line


def find_headers(lines):
    lines = list(lines)
    it_lines_1 = iter(lines)
    it_lines_2 = iter(lines)
    next(it_lines_2)
    pairs = zip(it_lines_1, it_lines_2)

    for prev, current  in pairs:
        #print(len(current.content), current.content)
        if len(current.content) == 1:
            sc = set(current.content[0])
            #print(f'{prev}|{current} -> ', sc)
            sc = set(current.content)
            yield Header(prev.content)
            next(pairs)
        else:
            yield prev





def parse(input):
    tokens =  list(tokenize(input))
    return (RepeatParser(
        OrParser(
            [NamedDirectiveParser(), DefaultDirectiveParser(), NoneParser()]
        )
    ).parse(tokens))
    #print(DefaultDirectiveParser().parse(tokens))
    return[]
    #print(tokens)
    #lines = list(find_headers(by_lines(tokens)))
    
    #return lines


if __name__ == '__main__':
    for p in parse(sample)[0]:
        pass
        print(p)
