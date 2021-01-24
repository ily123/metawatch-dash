"""Container for Blizzard class colors."""

from typing import List

import pandas as pd


class ClassColors:
    def __init__(self):
        # https://wow.gamepedia.com/Class_colors
        self.class_rgb_color = {
            "death knight": (196, 31, 59),
            "demon hunter": (163, 48, 201),
            "death_knight": (196, 31, 59),
            "demon_hunter": (163, 48, 201),
            "druid": (255, 125, 10),
            "hunter": (169, 210, 113),
            "mage": (64, 199, 235),
            "monk": (0, 255, 150),
            "paladin": (245, 140, 186),
            "priest": (255, 255, 255),
            "rogue": (255, 245, 105),
            "shaman": (0, 112, 222),
            "warlock": (135, 135, 237),
            "warrior": (199, 156, 110),
        }

    def get_rbg(self, class_name):
        """Returns color for given class."""
        return self.class_rgb_color[class_name.lower()]


class Specs:
    """Container for spec meta data.

    These are hard-coded. AFAIK, Blizzard never changes them.
    """

    def __init__(self):
        """Init of list of dict, where each dict is a spec."""
        class_colors = ClassColors()
        self.specs = []
        for index, row in enumerate(self.get_specs()):
            spec = dict(
                class_name=row[0],
                class_id=row[1],
                spec_name=row[2],
                spec_id=row[3],
                role=row[4],
                token=row[5],
                shorthand=row[6],
                color=class_colors.get_rbg(row[0]),
                index=index,
            )
            self.specs.append(spec)

    # I am not using a df here because the data is small
    # and df will just add overhead that isn't worth it
    def get_color(self, spec_id):
        """Get color for spec using spec id."""
        for spec in self.specs:
            if spec["spec_id"] == spec_id:
                return spec["color"]
        raise ValueError("spec id not found in spec table")

    def get_class_name(self, spec_id):
        """Get class name given a spec id."""
        for spec in self.specs:
            if spec["spec_id"] == spec_id:
                return spec["class_name"]
        raise ValueError("spec id not found in spec table")

    def get_spec_name(self, spec_id):
        """Get class name given a spec id."""
        for spec in self.specs:
            if spec["spec_id"] == spec_id:
                return spec["spec_name"]
        raise ValueError("spec id not found in spec table")

    def get_spec_name_by_token(self, spec_token):
        """Get class name given a spec token."""
        for spec in self.specs:
            if spec["shorthand"] == spec_token:
                return spec["token"]
        raise ValueError("spec id not found in spec table")

    def get_role(self, spec_id):
        """Get class name given a spec id."""
        for spec in self.specs:
            if spec["spec_id"] == spec_id:
                return spec["role"]
        raise ValueError("spec id not found in spec table")

    def get_spec_ids_for_role(self, role):
        """Get list of spec ids for role."""
        valid_roles = ["tank", "healer", "mdps", "rdps"]
        if role not in valid_roles:
            raise ValueError("Spec role invalid. Must be one of: %s")
        role_specs = []
        for spec in self.specs:
            if spec["role"] == role:
                role_specs.append(spec["spec_id"])
        return role_specs

    def vectorize_comp_token(self, token: str) -> List[int]:
        """Converts comp token to vector representation.

        Parameter
        ---------
        token : str
            string of characters a-zA-K where each char
            corresponds to a player spec

        Returns
        -------
        vector : list[int]
            vector encoding of the spec frequencies in the token
        """
        specs = self.get_specs()
        spec_index = dict(zip([spec[-1] for spec in specs], range(len(specs))))
        vector = [0] * len(specs)
        for spec_char in token:
            index = spec_index[spec_char]
            vector[index] += 1
        return vector

    @staticmethod
    def get_specs():
        """Returns nested list of spec meta data."""
        # fmt: off
        return [
            ['death knight', 6, 'blood', 250, 'tank', 'death_knight_blood', 'a'],
            ['death knight', 6, 'frost', 251, 'mdps', 'death_knight_frost', 'b'],
            ['death knight', 6, 'unholy', 252, 'mdps', 'death_knight_unholy', 'c'],
            ['demon hunter', 12, 'havoc', 577, 'mdps', 'demon_hunter_havoc', 'd'],
            ['demon hunter', 12, 'vengeance', 581, 'tank', 'demon_hunter_vengeance', 'e'],
            ['druid', 11, 'balance', 102, 'rdps', 'druid_balance', 'f'],
            ['druid', 11, 'feral', 103, 'mdps', 'druid_feral', 'g'],
            ['druid', 11, 'guardian', 104, 'tank', 'druid_guardian', 'h'],
            ['druid', 11, 'restoration', 105, 'healer', 'druid_restoration', 'i'],
            ['hunter', 3, 'beast mastery', 253, 'rdps', 'hunter_beast_mastery', 'j'],
            ['hunter', 3, 'marksmanship', 254, 'rdps', 'hunter_marksmanship', 'k'],
            ['hunter', 3, 'survival', 255, 'mdps', 'hunter_survival', 'l'],
            ['mage', 8, 'arcane', 62, 'rdps', 'mage_arcane', 'm'],
            ['mage', 8, 'fire', 63, 'rdps', 'mage_fire', 'n'],
            ['mage', 8, 'frost', 64, 'rdps', 'mage_frost', 'o'],
            ['monk', 10, 'brewmaster', 268, 'tank', 'monk_brewmaster', 'p'],
            ['monk', 10, 'mistweaver', 270, 'healer', 'monk_mistweaver', 'q'],
            ['monk', 10, 'windwalker', 269, 'mdps', 'monk_windwalker', 'r'],
            ['paladin', 2, 'holy', 65, 'healer', 'paladin_holy', 's'],
            ['paladin', 2, 'protection', 66, 'tank', 'paladin_protection', 't'],
            ['paladin', 2, 'retribution', 70, 'mdps', 'paladin_retribution', 'u'],
            ['priest', 5, 'discipline', 256, 'healer', 'priest_discipline', 'v'],
            ['priest', 5, 'holy', 257, 'healer', 'priest_holy', 'w'],
            ['priest', 5, 'shadow', 258, 'rdps', 'priest_shadow', 'x'],
            ['rogue', 4, 'assassination', 259, 'mdps', 'rogue_assassination', 'y'],
            ['rogue', 4, 'outlaw', 260, 'mdps', 'rogue_outlaw', 'z'],
            ['rogue', 4, 'subtlety', 261, 'mdps', 'rogue_subtlety', 'A'],
            ['shaman', 7, 'elemental', 262, 'rdps', 'shaman_elemental', 'B'],
            ['shaman', 7, 'enhancement', 263, 'mdps', 'shaman_enhancement', 'C'],
            ['shaman', 7, 'restoration', 264, 'healer', 'shaman_restoration', 'D'],
            ['warlock', 9, 'affliction', 265, 'rdps', 'warlock_affliction', 'F'],
            ['warlock', 9, 'demonology', 266, 'rdps', 'warlock_demonology', 'G'],
            ['warlock', 9, 'destruction', 267, 'rdps', 'warlock_destruction', 'H'],
            ['warrior', 1, 'arms', 71, 'mdps', 'warrior_arms', 'I'],
            ['warrior', 1, 'fury', 72, 'mdps', 'warrior_fury', 'J'],
            ['warrior', 1, 'protection', 73, 'tank', 'warrior_protection', 'K']
        ]
        # fmt: on


def vectorize_comps(composition: pd.DataFrame) -> pd.DataFrame:
    """Appends vector representation of each comp to the composition df.

    Parameter
    ---------
    composition : pd.DataFrame
        dataframe with following columns - tokenized comp name,
        number of runs by comp, average and std dev of the run
        key levels

    Returns
    -------
    composition_vectorized : pd.DataFrame
        original dataframe, plus 36 columns encoding spec frequencies
        for each comp
    """
    spec_util = Specs()
    comp_matrix = composition.apply(
        lambda row: spec_util.vectorize_comp_token(row["composition"]), axis=1
    )
    comp_matrix = pd.DataFrame(comp_matrix.values.tolist())
    comp_matrix.columns = [spec["token"] for spec in spec_util.specs]
    composition_vectorized = pd.concat([composition, comp_matrix], axis=1)
    return composition_vectorized


def get_full_comp(composition):
    spec_util = Specs()
    composition.reset_index(inplace=True)
    full_names = composition.apply(
        lambda row: sorted(
            [spec_util.get_spec_name_by_token(letter) for letter in row["composition"]]
        ),
        axis=1,
    )
    full_names = pd.DataFrame(full_names.values.tolist())
    full_names.columns = ["tank", "healer", "dps1", "dps2", "dps3"]
    comp_full_names = pd.concat([full_names, composition], axis=1)
    return comp_full_names
