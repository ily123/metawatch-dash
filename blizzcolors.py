"""Container for Blizzard class colors."""


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
        for row in self.get_specs():
            spec = dict(
                class_name=row[0],
                class_id=row[1],
                spec_name=row[2],
                spec_id=row[3],
                role=row[4],
                token=row[5],
                color=class_colors.get_rbg(row[0]),
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

    @staticmethod
    def get_specs():
        """Returns nested list of spec meta data."""
        # yapf: disable
        return [
            ['death knight', 6, 'blood', 250, 'tank', 'death_knight_blood'],
            ['death knight', 6, 'frost', 251, 'mdps', 'death_knight_frost'],
            ['death knight', 6, 'unholy', 252, 'mdps', 'death_knight_unholy'],
            ['demon hunter', 12, 'havoc', 577, 'mdps', 'demon_hunter_havoc'],
            ['demon hunter', 12, 'vengeance', 581, 'tank', 'demon_hunter_vengeance'],
            ['druid', 11, 'balance', 102, 'rdps', 'druid_balance'],
            ['druid', 11, 'feral', 103, 'mdps', 'druid_feral'],
            ['druid', 11, 'guardian', 104, 'tank', 'druid_guardian'],
            ['druid', 11, 'restoration', 105, 'healer', 'druid_restoration'],
            ['hunter', 3, 'beast mastery', 253, 'rdps', 'hunter_beast_mastery'],
            ['hunter', 3, 'marksmanship', 254, 'rdps', 'hunter_marksmanship'],
            ['hunter', 3, 'survival', 255, 'mdps', 'hunter_survival'],
            ['mage', 8, 'arcane', 62, 'rdps', 'mage_arcane'],
            ['mage', 8, 'fire', 63, 'rdps', 'mage_fire'],
            ['mage', 8, 'frost', 64, 'rdps', 'mage_frost'],
            ['monk', 10, 'brewmaster', 268, 'tank', 'monk_brewmaster'],
            ['monk', 10, 'mistweaver', 270, 'healer', 'monk_mistweaver'],
            ['monk', 10, 'windwalker', 269, 'mdps', 'monk_windwalker'],
            ['paladin', 2, 'holy', 65, 'healer', 'paladin_holy'],
            ['paladin', 2, 'protection', 66, 'tank', 'paladin_protection'],
            ['paladin', 2, 'retribution', 70, 'mdps', 'paladin_retribution'],
            ['priest', 5, 'discipline', 256, 'healer', 'priest_discipline'],
            ['priest', 5, 'holy', 257, 'healer', 'priest_holy'],
            ['priest', 5, 'shadow', 258, 'rdps', 'priest_shadow'],
            ['rogue', 4, 'assassination', 259, 'mdps', 'rogue_assassination'],
            ['rogue', 4, 'outlaw', 260, 'mdps', 'rogue_outlaw'],
            ['rogue', 4, 'subtlety', 261, 'mdps', 'rogue_subtlety'],
            ['shaman', 7, 'elemental', 262, 'rdps', 'shaman_elemental'],
            ['shaman', 7, 'enhancement', 263, 'mdps', 'shaman_enhancement'],
            ['shaman', 7, 'restoration', 264, 'healer', 'shaman_restoration'],
            ['warlock', 9, 'affliction', 265, 'rdps', 'warlock_affliction'],
            ['warlock', 9, 'demonology', 266, 'rdps', 'warlock_demonology'],
            ['warlock', 9, 'destruction', 267, 'rdps', 'warlock_destruction'],
            ['warrior', 1, 'arms', 71, 'mdps', 'warrior_arms'],
            ['warrior', 1, 'fury', 72, 'mdps', 'warrior_fury'],
            ['warrior', 1, 'protection', 73, 'tank', 'warrior_protection']
        ]
        # yapf: enable
