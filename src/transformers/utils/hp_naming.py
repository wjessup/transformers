# Define a class named TrialShortNamer
class TrialShortNamer:
    
    # Define class variables
    PREFIX = "hp"
    DEFAULTS = {}
    NAMING_INFO = None
    
    # Define a class method to set class variables 
    @classmethod
    def set_defaults(cls, prefix, defaults):
        cls.PREFIX = prefix
        cls.DEFAULTS = defaults
        cls.build_naming_info()

    # Define a static method to generate shortname for the given word
    @staticmethod
    def shortname_for_word(info, word):
        
        # If length of word is zero return an empty string
        if len(word) == 0:
            return ""
        
        # Raise exception if word contains any numerical characters
        if any(char.isdigit() for char in word):
            raise Exception(f"Parameters should not contain numbers: '{word}' contains a number")
        
        # If the word is in the list of short words, return the corresponding short word
        if word in info["short_word"]:
            return info["short_word"][word]
        
        # If above conditions fail, generate a new short word for the given word
        # Iterate from 1 to the length of the word and find the first prefix that is not present in the 
        # reverse_short_word list (dictionary)
        # If a prefix is not found, generate a new short word by concatenating the given word with '#' and
        # integer value of i
        # Add the generated short word to the short_word and reverse_short_word lists and return it 
        else:
            short_word = None
            for prefix_len in range(1, len(word) + 1):
                prefix = word[:prefix_len]
                if prefix in info["reverse_short_word"]:
                    continue
                else:
                    short_word = prefix
                    break
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
                        continue
                    else:
                        short_word = sword
                        break
            info["short_word"][word] = short_word
            info["reverse_short_word"][short_word] = word
            return short_word
    
    # Define a static method to generate shortname for the given parameter name
    @staticmethod
    def shortname_for_key(info, param_name):
        # Split the parameter name using '_' separator
        words = param_name.split("_")
        
        # Generate shortnames for each word in the parameter name
        shortname_parts = [TrialShortNamer.shortname_for_word(info, word) for word in words]

        # We try to create a separatorless short name, but if there is a collision we have to fallback
        # to a separated short name
        # Generate a short name by concatenating the short name parts using '' and '_' separators
        # Check if the generated short name already exists in the reverse_short_param list (dictionary).
        # If it does not exist, add the short name and parameter name to the respective lists and return the 
        # generated short name
        # else return the parameter name
        
        separators = ["", "_"]
        for separator in separators:
            shortname = separator.join(shortname_parts)
            if shortname not in info["reverse_short_param"]:
                info["short_param"][param_name] = shortname
                info["reverse_short_param"][shortname] = param_name
                return shortname
            
        return param_name
    
    # Define a static method to add new parameter name to short_param and reverse_short_param list
    @staticmethod
    def add_new_param_name(info, param_name):
        short_name = TrialShortNamer.shortname_for_key(info, param_name)
        info["short_param"][param_name] = short_name
        info["reverse_short_param"][short_name] = param_name

    # Define a class method to generate short names for all parameter names in the DEFAULTS list
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
    
    # Define a class method to generate the final short name of the trial
    @classmethod
    def shortname(cls, params):
        cls.build_naming_info()
        assert cls.PREFIX is not None
        name = [cls.PREFIX]

        for k, v in params.items():
            if k not in cls.DEFAULTS:
                raise Exception(f"You should provide a default value for the param name {k} with value {v}")
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

    # Define a class method to parse the trial short name and return the parameter dict
    @classmethod
    def parse_repr(cls, repr):
        # Remove the prefix from the short name and extract the parameter values from the short name
        repr = repr[len(cls.PREFIX) + 1 :]
        if repr == "":
            values = []
        else:
            values = repr.split("_")
        
        # Create a dictionary containing the parameter name and its corresponding value
        parameters = {}
        for value in values:
            if "-" in value:
                p_k, p_v = value.split("-")
            else:
                p_k = re.sub("[0-9.]", "", value)
                p_v = float(re.sub("[^0-9.]", "", value))

            # Update the parameter value in the dictionary
            key = cls.NAMING_INFO["reverse_short_param"][p_k]

            parameters[key] = p_v
        
        # Update parameters dictionary with default parameters
        for k in cls.DEFAULTS:
            if k not in parameters:
                parameters[k] = cls.DEFAULTS[k]

        return parameters