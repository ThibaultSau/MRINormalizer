import pandas
import re
import os

class MRIParser:
    """MRI sequence name parser, loads a csv file and decipher whether a specific sequence name is valid according to this file, and normalizes it.
    """
    def __init__(self):
        self.csv = None
        self.regexp = re.compile(".([0-9]*/?){3}.-.([0-9]*/?){3}.")

    def is_valid_sequence(self, sequence):
        """Check whether a specific sequence name is valid.
        
        A MRI sequence is considered valid if it is an axial or 3D acquisition, either T1 or T2.
        Water saturation, localizers, screenshots and fat saturation with no contrast injection are considered noot valid.

        Args:
            sequence (str): The sequence name to check

        Returns:
            bool: Whether the sequence name is considered valid.
        """
        try:
            sequence = self.csv.loc[
                sequence.split("_")[0]
                .lstrip(" 0123456789")
                .replace("  ", " ")
                .replace("  ", " ")
            ]
        except:
            return False

        if isinstance(sequence, pandas.core.frame.DataFrame):
            sequence = sequence.iloc[0]
        try:
            if sequence["Ponderation"]:
                t1_or_t2 = (
                    sequence["Ponderation"].lower() == "t1"
                    or sequence["Ponderation"].lower() == "t2"
                )
            else:
                t1_or_t2 = False
        except:
            raise
        if sequence["Plane"] or sequence["3D"]:
            ax = str(sequence["Plane"]).lower() == "ax" or sequence["3D"] == "3D"
        else:
            ax = False

        if "water sat" == sequence["Observation"]:
            return False
        if "loc" in str(sequence["Observation"]).lower():
            return False
        if "screenshot" in str(sequence["Observation"]).lower():
            return False
        if sequence["Injection"] and not sequence["Saturation"]:
            return False

        return t1_or_t2 and ax

    def standard_name(self, sequence):
        """Normalizes the sequence name according to a configuration file e.g. "WATER 3D T1 gADO" => T1 Inj Sat

        Args:
            sequence (str): a saquence name in the file

        Returns:
            str: the normalized sequence name
        """
        sequence = self.csv.loc[
            sequence.split("_")[0]
            .lstrip(" 0123456789")
            .replace("  ", " ")
            .replace("  ", " ")
        ]
        if isinstance(sequence, pandas.core.frame.DataFrame):
            sequence = sequence.iloc[0]
        name = f"{sequence['Ponderation']}"
        try:
            if sequence["Injection"]:
                name += " Inj"
        except:
            raise
        try:
            if sequence["Saturation"]:
                name += " Sat"
        except:
            raise
        if name == "DWI":
            if str(sequence["b (DWI)"]) == "ADC":
                return "ADC"

        return name

    def is_diff(self, sequence):
        """Checks whether the sequence is a 

        Args:
            sequence (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            sequence = self.csv.loc[
                sequence.split("_")[0]
                .lstrip(" 0123456789")
                .replace("  ", " ")
                .replace("  ", " ")
            ]
        except:
            return False
        return (
            str(sequence["Ponderation"]) == "DWI"
        )

    def is_perf(self, sequence):
        if "perf" in sequence.lower() or "dyn" in sequence.lower():
            return True
        try:
            sequence = self.csv.loc[
                sequence.split("_")[0]
                .lstrip(" 0123456789")
                .replace("  ", " ")
                .replace("  ", " ")
            ]
            if isinstance(sequence, pandas.core.frame.DataFrame):
                sequence = sequence.iloc[0]
        except:
            return False

        return (
            (self.regexp.match(sequence.name.strip("'")) is not None)
            or "perf" in sequence.name.lower()
            or "dyn" in sequence.name.lower()
            or "perf" in str(sequence["Observation"]).lower()
        )

    def load_csv(self, path):
        self.csv = (
            pandas.read_csv(os.path.join(path, "liste_sequence_eurad.csv"))
            .set_index("Sequence")
            .fillna(0)
        )
        return self