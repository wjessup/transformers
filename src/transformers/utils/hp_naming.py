# Setting up Trial Naming Convention
class TrialShortNamer:
    
    # defining prefix, default values and naming_info of experiment/trial
    PREFIX = "hp"
    DEFAULTS = {}
    NAMING_INFO = None

    # Function to set prefix and defaults
    @classmethod
    def set_defaults(cls, prefix, defaults):
        cls.PREFIX = prefix
        cls.DEFAULTS = defaults
        cls.build_naming_info()

    # Function to shorten a word
    @staticmethod
    def shortname_for_word(info, word):
        if not word:
            return ""
        if any(char.isdigit() for char in word):
            raise ValueError(f"Parameters should not contain numbers: '{word}' contains a number")
        # Assign a new variable to None
        short_word = None
        # If word exists on short_word dict, return its shortened version
        if word in info["short_word"]:
            return info["short_word"][word]
        # Shorten word by assigning prefix of the word to a new var until it is not in reverse_short_word dict
        for prefix_len in range(1, len(word) + 1):
            prefix = word[:prefix_len]
            if prefix in info["reverse_short_word"]:
                continue
            else:
                short_word = prefix
                break
        # If the word's prefix is already in reverse_short_word then add a combination of the word and a default value
        if short_word is None:
            def int_to_alphabetic(integer):
                s = ""
                while integer != 0:
                    s = chr(ord("A") + integer % 10) + s
                    integer //= 10
                return s
            i = 0
            while True:
                sword = word + "#" + int_to_alphabetic(i)
                if sword in info["reverse_short_word"]:
                    i += 1
                    continue
                else:
                    short_word = sword
                    break
        # Update info dicts with new values
        info["short_word"][word] = short_word
        info["reverse_short_word"][short_word] = word
        # Return shortened version of the word
        return short_word

    # Use shortname_for_words() to shorten parameter names and add to naming_info dict
    @staticmethod
    def shortname_for_key(info, param_name):
        # Use '_' to split parameter names into words
        words = param_name.split("_")
        # Shorten individual words and add them back to a shortened parameter name
        shortname_parts = [TrialShortNamer.shortname_for_word(info, word) for word in words]
        separators = ["", "_"]
        # Shortened name is either separator-less or uses '_' as a separator
        for separator in separators:
            shortname = separator.join(shortname_parts)
            # If name is not in reverse_short_param dict we add it
            if shortname not in info["reverse_short_param"]:
                info["short_param"][param_name] = shortname
                info["reverse_short_param"][shortname] = param_name
                return shortname
        return param_name

    #Add a new parameter to naming_info dict
    @staticmethod
    def add_new_param_name(info, param_name):
        short_name = TrialShortNamer.shortname_for_key(info, param_name)
        info["short_param"][param_name] = short_name
        info["reverse_short_param"][short_name] = param_name

    # Create naming_info dict using defaults
    @classmethod
    def build_naming_info(cls):
        if cls.NAMING_INFO is not None:
            return
        info = {
            "short_word": {},
            "reverse_short_word": {},
            "short_param": {},
            "reverse_short_param": {},
        }
        field_keys = list(cls.DEFAULTS.keys())
        for k in field_keys:
            cls.add_new_param_name(info, k)
        cls.NAMING_INFO = info

    # Function to create a short name for trial/experiment by appending the parameters and values
    # from the experiment to a prefix with an underscore in between
    @classmethod
    def shortname(cls, params):
        cls.build_naming_info()
        assert cls.PREFIX is not None
        name = [cls.PREFIX]

        for k, v in params.items():
            if k not in cls.DEFAULTS:
                raise ValueError(f"You should provide a default value for the param name {k} with value {v}")
            if v == cls.DEFAULTS[k]:
                # The default value is not added to the name
                continue

            key = cls.NAMING_INFO["short_param"][k]

            if isinstance(v, bool):
                v = 1 if v else 0

            sep = "" if isinstance(v, (int, float)) else "-"
            e = f"{key}{sep}{v}"
            name.append(e)

        return "_".join(name)

    #Function parse short name into parameters and values
    @classmethod
    def parse_repr(cls, repr):
        repr = repr[len(cls.PREFIX) + 1 :]
        values = repr.split("_") if repr else []
        parameters = {}
        for value in values:
            # If value is separated by '-' in shortened name, it means the value is numeric (int/float)
            if "-" in value:
                p_k, p_v = value.split("-")
            else:
                # Get parameter_name by removing numbers and periods from string
                p_k = re.sub("[0-9.]", "", value)
                # Get parameter_value by keeping only the numbers and periods
                p_v = float(re.sub("[^0-9.]", "", value))

            key = cls.NAMING_INFO["reverse_short_param"][p_k]

            parameters[key] = p_v

        for k in cls.DEFAULTS:
            if k not in parameters:
                parameters[k] = cls.DEFAULTS[k]

        return parameters