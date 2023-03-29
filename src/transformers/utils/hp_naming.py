import copy
import re

class TrialShortNamer:
    PREFIX = "hp"
    DEFAULTS = {}
    NAMING_INFO = None

    @classmethod
    def set_defaults(cls, prefix, defaults):
        cls.PREFIX = prefix
        cls.DEFAULTS = defaults
        cls.build_naming_info()

    @staticmethod
    def shortname_for_word(info, word):
        if not word:
            return ""
        if any(char.isdigit() for char in word):
            raise Exception(f"Parameters should not contain numbers: '{word}' contains a number")
        if word in info["short_word"]:
            return info["short_word"][word]
        for prefix_len in range(1, len(word) + 1):
            prefix = word[:prefix_len]
            if prefix not in info["reverse_short_word"]:
                return prefix
        i = 0
        while True:
            sword = word + "#" + chr(ord("A") + i % 10)
            if sword not in info["reverse_short_word"]:
                return sword
            i += 1

    @staticmethod
    def shortname_for_key(info, param_name):
        words = param_name.split("_")
        shortname_parts = [TrialShortNamer.shortname_for_word(info, word) for word in words]
        shortname = "".join(shortname_parts)
        suffix = ""
        while shortname + suffix in info["reverse_short_param"]:
            suffix = str(int(suffix or 0) + 1)
        shortname += suffix
        info["short_param"][param_name] = shortname
        info["reverse_short_param"][shortname] = param_name
        return shortname

    @classmethod
    def build_naming_info(cls):
        if cls.NAMING_INFO:
            return
        info = {
            "short_word": {},
            "reverse_short_word": {},
            "short_param": {},
            "reverse_short_param": {},
        }
        for k in cls.DEFAULTS:
            TrialShortNamer.shortname_for_key(info, k)
        cls.NAMING_INFO = info

    @classmethod
    def shortname(cls, params):
        cls.build_naming_info()
        assert cls.PREFIX is not None
        name = [copy.copy(cls.PREFIX)]
        for k, v in params.items():
            if k not in cls.DEFAULTS:
                raise Exception(f"You should provide a default value for the param name {k} with value {v}")
            if v == cls.DEFAULTS[k]:
                continue
            key = cls.NAMING_INFO["short_param"][k]
            v = 1 if isinstance(v, bool) and v else v
            name.append(f"{key}-{v}")
        return "_".join(name)

    @classmethod
    def parse_repr(cls, repr_args):
        repr_args = repr_args[len(cls.PREFIX) + 1:]
        if not repr_args:
            return cls.DEFAULTS.copy()
        params = {}
        for arg in repr_args.split("_"):
            key, value = re.split(r"(-)(?=[^-\d\.])", arg)
            value = float(value)
            key = cls.NAMING_INFO["reverse_short_param"][key]
            params[key] = int(value) if value.is_integer() else value
        for k in cls.DEFAULTS:
            if k not in params:
                params[k] = cls.DEFAULTS[k]
        return params