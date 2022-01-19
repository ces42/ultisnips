from test.constant import *
from test.vim_test_case import VimTestCase as _VimTest


class ContextSnippets_SimpleSnippet(_VimTest):
    files = {
        "us/all.snippets": r"""
        snippet a "desc" "True" e
        abc
        endsnippet
        """
    }
    keys = "a" + EX
    wanted = "abc"


class ContextSnippets_ExpandOnTrue(_VimTest):
    files = {
        "us/all.snippets": r"""
        global !p
        def check_context():
            return True
        endglobal

        snippet a "desc" "check_context()" e
        abc
        endsnippet
        """
    }
    keys = "a" + EX
    wanted = "abc"


class ContextSnippets_DoNotExpandOnFalse(_VimTest):
    files = {
        "us/all.snippets": r"""
        global !p
        def check_context():
            return False
        endglobal

        snippet a "desc" "check_context()" e
        abc
        endsnippet
        """
    }
    keys = "a" + EX
    wanted = keys


class ContextSnippets_UseContext(_VimTest):
    files = {
        "us/all.snippets": r"""
        global !p
        def wrap(ins):
            return "< " + ins + " >"
        endglobal

        snippet a "desc" "wrap(snip.buffer[snip.line])" e
        { `!p snip.rv = context` }
        endsnippet
        """
    }
    keys = "a" + EX
    wanted = "{ < a > }"


class ContextSnippets_SnippetPriority(_VimTest):
    files = {
        "us/all.snippets": r"""
        snippet i "desc" "re.search('err :=', snip.buffer[snip.line-1])" e
        if err != nil {
            ${1:// pass}
        }
        endsnippet

        snippet i
        if ${1:true} {
            ${2:// pass}
        }
        endsnippet
        """
    }

    keys = (
        r"""
        err := some_call()
        i"""
        + EX
        + JF
        + """
        i"""
        + EX
    )
    wanted = r"""
        err := some_call()
        if err != nil {
            // pass
        }
        if true {
            // pass
        }"""


class ContextSnippets_PriorityKeyword(_VimTest):
    files = {
        "us/all.snippets": r"""
        snippet i "desc" "True" e
        a
        endsnippet

        priority 100
        snippet i
        b
        endsnippet
        """
    }

    keys = "i" + EX
    wanted = "b"


class ContextSnippets_ReportError(_VimTest):
    files = {
        "us/all.snippets": r"""
        snippet e "desc" "Tru" e
        error
        endsnippet
        """
    }

    keys = "e" + EX
    wanted = "e" + EX
    expected_error = r"NameError: name 'Tru' is not defined"


class ContextSnippets_ReportErrorOnIndexOutOfRange(_VimTest):
    # Working around: https://github.com/neovim/python-client/issues/128.
    skip_if = lambda self: "Bug in Neovim." if self.vim_flavor == "neovim" else None
    files = {
        "us/all.snippets": r"""
        snippet e "desc" "snip.buffer[123]" e
        error
        endsnippet
        """
    }

    keys = "e" + EX
    wanted = "e" + EX
    expected_error = r"IndexError: line number out of range"


class ContextSnippets_CursorIsZeroBased(_VimTest):
    files = {
        "us/all.snippets": r"""
        snippet e "desc" "snip.cursor" e
        `!p snip.rv = str(snip.context)`
        endsnippet
        """
    }

    keys = "e" + EX
    wanted = "(2, 1)"


class ContextSnippets_ContextIsClearedBeforeExpand(_VimTest):
    files = {
        "us/all.snippets": r"""
        pre_expand "snip.context = 1 if snip.context is None else 2"
        snippet e "desc" w
        `!p snip.rv = str(snip.context)`
        endsnippet
        """
    }

    keys = "e" + EX + " " + "e" + EX
    wanted = "1 1"


class ContextSnippets_ContextHasAccessToVisual(_VimTest):
    files = {
        "us/all.snippets": r"""
        snippet test "desc" "snip.visual_text == '123'" we
        Yes
        endsnippet

        snippet test "desc" w
        No
        endsnippet
        """
    }

    keys = (
        "123" + ESC + "vhh" + EX + "test" + EX + " zzz" + ESC + "vhh" + EX + "test" + EX
    )
    wanted = "Yes No"


class ContextSnippets_Header_ExpandOnTrue(_VimTest):
    files = {
        "us/all.snippets": r"""
        global !p
        def check_context():
            return True
        endglobal

        context "check_context()"
        snippet a "desc" e
        abc
        endsnippet
        """
    }
    keys = "a" + EX
    wanted = "abc"


class ContextSnippets_Header_DoNotExpandOnFalse(_VimTest):
    files = {
        "us/all.snippets": r"""
        global !p
        def check_context():
            return False
        endglobal

        context "check_context()"
        snippet a "desc" e
        abc
        endsnippet
        """
    }
    keys = "a" + EX
    wanted = keys

class ContextSnippets_LotsOfGlobals(_VimTest):
    files = {
        "us/all.snippets": r'''
        global !p
        def check_context():
            return False

        def math():
            return vim.api.eval('vimtex#syntax#in_mathzone()')

        def has_text(s):
            return bool(s) and not s.isspace()

        def check_newline():
            line = snip.buffer[snip.line]
            left = has_text(line[:snip.cursor[1]-1])
            right = has_text(line[snip.cursor[1]:])
            indent = re.match(r'\s*', line).group(0)
            return [left, right, indent]

        def comment():
            return vim.api.eval('vimtex#syntax#in_comment()')

        def env(*names):
            for name in names:
                [x,y] = vim.api.eval("vimtex#env#is_inside('" + name + "')")
                if x and y:
                    return True
            return False

        #ATOM = re.compile(r'\\[a-zA-Z]+|\S')
        #is_atomic = ATOM.fullmatch
        is_atomic = lambda s: re.fullmatch(r'(\\[a-zA-Z]+|\S)', s)

        LIMIT_COMMANDS = {'\\int', '\\iint', '\\iiint', '\\oint', '\\sum', '\\prod', '\\bigcup',
        '\\bigcap', '\\bigoplus', '\\bigotimes', '\\big', '\\bigvee', '\\bigwedge', '\\bigodot'}

        #TRANSLATE_TEX_UNICODE = vim.api.eval("exists('b:translate_tex_unicode') && b:translate_tex_unicode")
        def translate_tex_unicode():
            return vim.api.eval("exists('b:translate_tex_unicode') && b:translate_tex_unicode")

        def subseteq():
            return '⊆' if translate_tex_unicode() else '\\subseteq'

        def partial():
            return '∂' if translate_tex_unicode() else '\\partial'

        def norm():
            return '∥' if translate_tex_unicode() else '\\|'

        def forall():
            return '∀' if translate_tex_unicode() else '\\forall'
        #def exists():
        #	return '∃' if translate_tex_unicode() else '\\exists'

        def geq():
            return '≥' if translate_tex_unicode() else '\\geq'

        def leq():
            return '≤' if translate_tex_unicode() else '\\leq'

        def lesssim():
            return '≲' if translate_tex_unicode() else '\\lesssim'

        def gtrsim():
            return '≳' if translate_tex_unicode() else '\\gtrsim'

        def create_table(snip):
            rows = snip.buffer[snip.line].split('x')[0]
            cols = snip.buffer[snip.line].split('x')[1]

            int_val = lambda string: int(''.join(s for s in string if s.isdigit()))

            rows = int_val(rows)
            cols = int_val(cols)

            offset = cols + 1
            old_spacing = snip.buffer[snip.line][:snip.buffer[snip.line].rfind('\t') + 1]

            snip.buffer[snip.line] = ''

            final_str = old_spacing + "\\begin{tabular}{|" + "|".join(['$' + str(i + 1) for i in range(cols)]) + "|}\n"

            for i in range(rows):
                final_str += old_spacing + '\t'
                final_str += " & ".join(['$' + str(i * cols + j + offset) for j in range(cols)])

                final_str += " \\\\\\\n"

            final_str += old_spacing + "\\end{tabular}\n$0"

            snip.expand_anon(final_str)

        def add_row(snip):
            row_len = int(''.join(s for s in snip.buffer[snip.line] if s.isdigit()))
            old_spacing = snip.buffer[snip.line][:snip.buffer[snip.line].rfind('\t') + 1]

            snip.buffer[snip.line] = ''

            final_str = old_spacing
            final_str += " & ".join(['$' + str(j + 1) for j in range(row_len)])
            final_str += " \\\\\\"

            snip.expand_anon(final_str)

        endglobal

        context "check_context()"
        snippet a "desc" e
        abc
        endsnippet

        '''
    }
    keys = "a" + EX
    keys = keys*500
    wanted = keys
