import re, json

class CLICmdException(Exception):
    """ Base Exception Class for all CLI Command Execution Exceptions """
    type = ''
    pass

class CLICmdNormal(CLICmdException):
    """ Info Level Exception of CLI Command Execution - This is a Successful Execution """
    is_error=False

class ANCLIParser(object):
    """ Base class for legacy CLI parsers """
    def __init__(self, exclusive=False, supplement=False):
        self.exclusive = exclusive
        self.supplement = supplement

    def parse(self, cmd_output):
        """ This function should be overwritten by subclasses.
        Parse a CLI output and return parsing results.

        Generally, a ``parse`` function does two things to report the CLI result:

        * To return result data, which is later collected and returned by :py:func:`cli_parse`
        * To raise exceptions (of type :py:exc:`CLICmdException`), which are collected and raised as a ``ModelQueryException`` by :py:func:`cli_parse`
        """
        raise TypeError('This function should be overwritten.')

class EasyParser(ANCLIParser):
    """ A easy parser splitting command output lines with spaces, and match these data with a given ``match_list``.

    :param prefix: A prefix string for the parser to match first. An output line is directly ignored if it doesn't match the prefix.
    :type  prefix: str

    :param match_list: A list of matching rules (string) for analyzing the output line (cutting the prefix).
                       The format of each rule string is "?<field_name>" which means specific data is fetched to the field; or "=<target_value>" which 
                       means specific data must equals the target data or else the line is ignored.
    :type  match_list: list of str
    """
    def __init__(self, prefix=None, match_list=None, strict_prefix=False, **kwargs):
        super(EasyParser, self).__init__(**kwargs)
        self._prefix = prefix or ""
        self._match_list = match_list
        self._strict_prefix = strict_prefix
        for each in self._match_list:
            if each[0] not in '?=':
                raise ValueError('invalid format in match_list of EasyParser %s' % each)

    def parse(self, cmd_output):
        result = []
        for line in cmd_output.split('\n'):
            line_result = self._parse_line(line)
            if line_result:
                result.append(line_result)
        return result

    def _parse_line(self, cmd_output):
        index = cmd_output.find(self._prefix)
        final_list = []
        result = {}
        if index == -1:
            return None
        else:
            if self._strict_prefix and index > 0:
                # in strict_prefix mode, match prefix from the beginning
                return None
            handle_list = cmd_output[index+len(self._prefix):].split(' ')
            in_quote = False
            quoted_string = ""
            for each in handle_list:
                if not each:
                    continue
                if not in_quote:
                    if each[0] == '"' and each[-1] == '"':
                        final_list.append(each[1:-1])
                    elif each[0] == '"':
                        in_quote = True
                        quoted_string += each[1:]
                    elif each[-1] == '"':
                        assert 0,"Incoupled quotes at CLI response %s" % cmd_output 
                    else:
                        final_list.append(each)
                else:
                    if each[-1] == '"':
                        quoted_string += (' ' + each[:-1])
                        in_quote = False
                        final_list.append(quoted_string)
                        quoted_string = ""
                    elif each[0] == '"' and len(each) > 1:
                        assert 0, "Incoupled quotes at CLI response %s" % cmd_output 
                    else:
                        quoted_string += (' ' + each)

        for index in range(0, len(final_list)):
            if not final_list[index] or index > len(self._match_list)-1 or not self._match_list[index]:
                continue
            mark = self._match_list[index][0]
            if mark == '?':
                result[self._match_list[index][1:]] = final_list[index]
            elif mark == '=':
                if not self._match_list[index][1:] == final_list[index]:
                    return None
            else:
                assert 0, "invalid format in match_list"
        
        # if there are left items in the _match_list, just set them to None
        # the later process of Model layer will set them to default values
        index += 1
        while index < len(self._match_list):
            result[self._match_list[index][1:]] = None
            index += 1

        return result
                

class BlankParser(ANCLIParser):
    """ Parser that checks whether the output of command is empty and raise exceptions as necessary.

    :param blank_exception: The exception to raise if the output is blank.
    :type  blank_exception: :py:class:`CLICmdException`
    :param nonblank_exception: The exception to raise if the output is not blank.
    :type  nonblank_exception: :py:class:`CLICmdException`
    :param blank_msg: The message for the exception to use. If not provided, the exception will use the whole output as msg.
    :type  blank_msg: str
    :param nonblank_msg: Similar as blank_msg but at non-blank case.
    :type  nonblank_msg: str
    """
    def __init__(self, blank_exception=None, nonblank_exception=None, blank_msg=None, nonblank_msg=None, **kwargs):
        super(BlankParser, self).__init__(**kwargs)
        self._blank_exception = blank_exception
        self._nonblank_exception = nonblank_exception
        self._blank_msg = blank_msg
        self._nonblank_msg = nonblank_msg

    def parse(self, cmd_output):
        if len(cmd_output.strip()):
            if self._nonblank_exception:
                andebug('hive.debug', 'raising nonblank exception with msg: %s' % cmd_output)
                raise self._nonblank_exception(self._nonblank_msg if self._nonblank_msg else cmd_output)
        else:
            if self._blank_exception:
                raise self._blank_exception(self._blank_msg if self._blank_msg else cmd_output)
        return cmd_output


class WHOLE:
    pass
class DICT:
    pass
class LIST:
    pass
class RAW:
    pass
class AUTO:
    pass
class MATCHONE:
    pass
class MATCHALL:
    pass

class RegexParser(ANCLIParser):
    """ A Parser matching the output with a regex pattern and return results.

    :param regex: The regex pattern string.
    :type  regex: str

    :param mode: ``MATCHONE`` to acquire data only from the first match; ``MATCHALL`` to match multiple places from the output and return a list of data.
    :type  mode: ``MATCHONE | ``MATCHALL``

    :param result: The format of returning data (or each item in the returning data list when mode is ``MATCHALL``.
                   * ``WHOLE`` - The whole match (a string) is returned
                   * ``DICT`` - The data is a dictionary containing matching attributes based on the ``(?P<field_name>)``-style pattern.
                   * ``LIST`` - The data is a list containing matching attributes acquired by the Python ``re`` libraries ``groups()`` API.
                   * ``AUTO`` - If any (?P<field_name>) pattern is found in the pattern, ``DICT`` is used, else ``LIST`` is used. 
                   * ``RAW`` - The data is a raw Python ``re`` ``match_object`` for the caller to analyze the data.
    :type  result: ``DICT`` | ``LIST`` | ``AUTO`` | ``RAW``

    :param match_exception: Exception to raise when the regex pattern matches.
    :type  match_exception: :py:class:`CLICmdException`

    :param unmatch_exception: Exception to raise when the regex pattern doesn't match.
    :type  unmatch_exception: :py:class:`CLICmdException`

    :param reflags: RE flags transmitted to the ``re.compile`` function

    :param match_msg: The message for the exception to use. If not provided, the exception will use the whole output as msg.
    :type  match_msg: str

    :param unmatch_msg: Similar as match_msg but at unmatch case.
    :type  unmatch_msg: str
    """
    def __init__(self, regex, mode=MATCHONE, result=AUTO, match_exception=None, unmatch_exception=None, reflags=0, match_msg=None, unmatch_msg=None, **kwargs):
        super(RegexParser, self).__init__(**kwargs)
        self._regex = re.compile(regex, reflags) if type(regex) in (str, unicode) else regex
        self._match_exception = match_exception
        self._unmatch_exception = unmatch_exception
        self._match_msg = match_msg
        self._unmatch_msg = unmatch_msg
        self._mode = mode
        self._result = result

    def parse(self, cmd_output):
        if self._mode == MATCHONE:
            match_obj = self._regex.search(cmd_output)

            if self._result == AUTO:
                if len(self._regex.groupindex) == 0:
                    if self._regex.groups == 0:
                        result = WHOLE
                    else:
                        result = LIST
                else:
                    result = DICT
            else:
                result = self._result

            if not match_obj:
                if self._unmatch_exception:
                    raise self._unmatch_exception(self._unmatch_msg if self._unmatch_msg else cmd_output)
                if result == LIST:
                    return []
                elif result == DICT:
                    return {}
                else:
                    return None
            else:
                if self._match_exception:
                    raise self._match_exception(self._match_msg if self._match_msg else cmd_output)

            if result == LIST:
                return match_obj.groups()
            elif result == WHOLE:
                return match_obj.group(0)
            elif result == DICT:
                return match_obj.groupdict()
            elif result == RAW:
                return match_obj
            else:
                raise ValueError
                
        elif self._mode == MATCHALL:
            match_obj = self._regex.finditer(cmd_output)
            empty = True

            matches = []
            for each_obj in match_obj:
                empty = False
                if self._result == AUTO:
                    if len(self._regex.groupindex) == 0:
                        if self._regex.groups == 0:
                            result = WHOLE
                        else:
                            result = LIST
                    else:
                        result = DICT
                else:
                    result = self._result

                if result == LIST:
                    matches.append(each_obj.groups())
                elif result == WHOLE:
                    matches.append(each_obj.group(0))
                elif result == DICT:
                    matches.append(each_obj.groupdict())
                elif result == RAW:
                    matches.append(each_obj)
                else:
                    raise ValueError

        # raise necessary exception
            if empty:
                if self._unmatch_exception:
                    raise self._unmatch_exception(self._unmatch_msg if self._unmatch_msg else cmd_output)
            else:
                if self._match_exception:
                    raise self._match_exception(self._match_msg if self._match_msg else cmd_output)

            return matches
        else:
            raise ValueError
            

def cli_parse(cmd_output, parser_obj):
    """ Implementation of the CLI output parser **workflow**

    **parser_obj** could be a single :py:class:`ANCLIParser` or a list of it.
    
    If it's a single parser, the parser will ``parse()`` the command output and return the result as defined in the parser.
    If it's a parser list, the parsers will call their own ``parse()`` functions one by one over the same ``cmd_output``, and 
    all results are collected into a list and returned.

    When exception happens, generally, this function will gather all exceptions (of type ``CLICmdExceptipn``) raised by parsers and raise a 
    ``ModelQueryException``. That is, an parser exception won't stop the workflow from iterating the next parser. However, there're two special
    cases based on the parser's settings:

    * If a parser has a ``supplement`` attribute, it will be directly ignored if there be any exception raised before the workflow arrives to it.
    * If a parser has a ``exclusive`` attribute, when it raises some exception, the workflow will stop and pass all left parsers.
    """
    if not parser_obj:
        return cmd_output
    elif isinstance(parser_obj, ANCLIParser):
        try:
            return parser_obj.parse(cmd_output)
        except CLICmdException, e:
            andebug('hive.debug', 'raising ModelQueryException with e: %s' % e)
            raise ModelQueryException(e)
    elif type(parser_obj) is list:
        res = []
        exceptions = []
        for each in parser_obj:
            if not isinstance(each, ANCLIParser):
                raise TypeError('Third argument of cmd should be an ANCLIParser or dict/list of it')
            # if this is a supplement parser, pass directly if there's already previous exception
            if each.supplement and exceptions:
                continue
            try:
                res.append(each.parse(cmd_output))
            except CLICmdException, e:
                if e.__class__ != CLICmdNormal:
                    res.append(None)
                    exceptions.append(e)
                # pass all left parsers if it's exclusive
                if each.exclusive:
                    break
        if exceptions:
            andebug('hive.debug', 'raising ModelQueryException with exceptions: %s' % exceptions)
            raise ModelQueryException(exceptions)
        return res
    else:
        raise TypeError('Third argument of cmd should be an ANCLIParser or list of it')

def EasyParserTest():
    output = """snmp on default 
    snmp community public
    snmp contact 
    snmp location 
    snmp enable traps
    snmp host 10.8.11.20 2 "public"
    snmp host 10.8.11.21 2 "public"
    snmp host 10.8.11.22 2 "array"
    snmp ipcontrol off
    """
    parse = EasyParser('snmp host', ['?ip', '?version', '=public', '?user'])
    data = cli_parse(output, parse)
    print(data)  # [{'ip': '10.8.11.20', 'version': '2', 'user': None}, {'ip': '10.8.11.21', 'version': '2', 'user': None}]

def RegexParserTest():
    parse_virtual_list = [ 
        RegexParser('slb virtual (?P<protocol>.*?) "(?P<service_name>.*?)" (?P<virtual_ip>[0-9|\.|:|a-f|A-F]+) (?P<virtual_port>[0-9]+) (?P<end>.*?)', MATCHALL),
        RegexParser('slb virtual disable (?P<service_name>.*?)', MATCHALL),
        RegexParser('slb virtual (?P<protocol>l2ip|ip|tuxedo) "(?P<service_name>.*?)" (?P<virtual_ip>[0-9|\.|:|a-f|A-F]+)', MATCHALL),
    ]  
    output = """
        slb virtual tcp "tcp_vs1" 10.4.72.6 80 arp 0
        slb virtual udp "us1" 10.4.72.18 53 arp 0
        slb virtual ftps "ftps1" 10.4.72.13 990 0
        slb virtual http "http_ampnew" 6.6.6.6 80 arp 0
        slb virtual http "http_vs2" 10.4.72.7 80 arp 0
        slb virtual http "http_vs7" 10.4.72.5 80 arp 0
        slb virtual http "vs1" 10.4.72.12 80 arp 0
        slb virtual https "https" 10.4.134.91 443 arp 0
        slb virtual https "https_vs2" 10.4.72.7 443 arp 0
        slb virtual tcps "vstcps" 10.4.71.21 53 arp 0
        slb virtual ip "ipip" 10.4.72.16 0
        slb virtual siptcp "vss1" 10.4.72.15 5060 arp 0
        slb virtual rdp "rd1" 10.4.72.15 3389 arp 0
        slb virtual diameter "dv1" 10.4.72.17 3868 arp 0
        slb virtual tuxedo "ts1" 10.4.72.14 0
    """
    #data[0] [{'service_name': 'tcp_vs1', 'end': '', 'virtual_ip': '10.4.72.6', 'protocol': 'tcp', 'virtual_port': '80'} ... ]
    #data[1] []
    #data[2] [{'service_name': 'ipip', 'protocol': 'ip', 'virtual_ip': '10.4.72.16'}, {'service_name': 'ts1', 'protocol': 'tuxedo', 'virtual_ip': '10.4.72.14'}]
    data = cli_parse(output, parse_virtual_list)   # data[i] 是parse_virtual_list[i] 的结果, 数组类型
    for item in data:
        print(item)

if __name__ == '__main__':
    #EasyParserTest()
    RegexParserTest()

