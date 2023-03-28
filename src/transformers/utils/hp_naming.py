import copy
import re

class TrialShortNamer:
    PREFIX = "hp"
    DEFAULTS = {}

    @staticmethod
    def set_defaults(prefix, defaults):
        TrialShortNamer.PREFIX, TrialShortNamer.DEFAULTS = prefix, defaults
        TrialShortNamer.build_naming_info()

    @staticmethod
    def int_to_alphabetic(integer):
        s = ""
        while integer != 0:
            s = chr(ord("A") + integer % 10) + s
            integer //= 10
        return s

    @staticmethod
    def shortname_for_word(info, word):
        if not word:
            return ""
        if any(char.isdigit() for char in word):
            raise Exception(f"Parameters should not contain numbers: '{word}' contains a number")
        if (short_word := info["short_word"].get(word)):
            return short_word
        for prefix_len in range(1, len(word) + 1):
            prefix = word[:prefix_len]
            if prefix in info["reverse_short_word"]:
                continue
            short_word = prefix
            break
        else:
            i = 0
            while True:
                sword = word + "#" + TrialShortNamer.int_to_alphabetic(i)
                if sword in info["reverse_short_word"]:
                    continue
                short_word = sword
                break
        info["short_word"][word] = short_word
        info["reverse_short_word"][short_word] = word
        return short_word

    @staticmethod
    def shortname_for_key(info, param_name):
        words = param_name.split("_")
        shortname_parts = [TrialShortNamer.shortname_for_word(info, word) for word in words]
        for separator in ("", "_"):
            shortname = separator.join(shortname_parts)
            if shortname not in info["reverse_short_param"]:
                info["short_param"][param_name] = shortname
                info["reverse_short_param"][shortname] = param_name
                return shortname
        return param_name

    @staticmethod
    def add_new_param_name(info, param_name):
        short_name = TrialShortNamer.shortname_for_key(info, param_name)
        info["short_param"][param_name] = short_name
        info["reverse_short_param"][short_name] = param_name

    @classmethod
    def build_naming_info(cls):
        if cls.DEFAULTS:
            cls.NAMING_INFO = {
                "short_word": {},
                "reverse_short_word": {},
                "short_param": {},
                "reverse_short_param": {},
            }
            for k in cls.DEFAULTS:
                cls.add_new_param_name(cls.NAMING_INFO, k)

    @classmethod
    def shortname(cls, params):
        assert cls.PREFIX is not None
        name = [copy.copy(cls.PREFIX)]
        for k, v in params.items():
            if k not in cls.DEFAULTS:
                raise Exception(f"You should provide a default value for the param name {k} with value {v}")
            if v == cls.DEFAULTS[k]:
                continue
            key = cls.NAMING_INFO["short_param"][k]
            sep = "" if isinstance(v, (int, float)) else "-"
            name.append(f"{key}{sep}{v}")
        return "_".join(name)

    @classmethod
    def parse_repr(cls, repr):
        repr = repr[len(cls.PREFIX)+1:]
        values = repr.split("_") if repr else []
        parameters = {}
        for value in values:
            if "-" in value:
                p_k, p_v = value.split("-")
                p_v = float(re.sub("[^0-9.]", "", p_v))
            else:
                p_k = re.sub("[0-9.]", "", value)
                p_v = float(re.sub("[^0-9.]", "", value))
            key = cls.NAMING_INFO["reverse_short_param"][p_k]
            parameters[key] = p_v
        for k in cls.DEFAULTS:
            if k not in parameters:
                parameters[k] = cls.DEFAULTS[k]
        return parameters