import os

import pandas as pd


class BritishMuseum:

    def __init__(self):
        self.path = "/home/fabian/Documents/cozy/Coin Project/european coins 1000bc-900ad"
        self.file_name = "megred_data.xlsx"
        self.data = pd.DataFrame()

    def __load_data(self):
        for file in os.listdir(self.path):
            if file.endswith(".csv"):
                file_path = os.path.join(self.path, file)
                df = pd.read_csv(file_path)
                self.data = self.data.append(df, ignore_index=True)

        self.data.drop_duplicates(subset="Museum number", inplace=True)

    def __drop_empty_cols(self):
        empty_cols = []
        for col in self.data.columns:
            if self.data[col].isna().all():
                empty_cols.append(col)

        self.data.drop(columns=empty_cols, inplace=True)

    def __clean_object_types(self):
        object_types = self.df['Object type'].str.split("; ", expand=True)

        object_types.columns = ['object_type1', 'object_type2', 'object_type3',
                                'object_type4']

        irrelevant_object_types = ['chatelaine', 'coin pendant', 'brooch',
                                   'chain',
                                   'pendant', 'coin brooch', 'bead',
                                   'finger-ring',
                                   'love token', 'medal', 'necklace',
                                   'disc brooch',
                                   'pseudo-coin brooch', 'pseudo-coin pendant',
                                   'medallion', 'seal', 'die', 'body chain',
                                   'stud',
                                   'trial-piece', 'ear-ring',
                                   'pseudo-coin brooch',
                                   'torc', 'hacksilver', 'sealing',
                                   'arrow-head',
                                   'jewellery', 'frame', 'disc', 'mount']

        for object_type in irrelevant_object_types:
            for col in object_types.columns:
                object_types = object_types.loc[
                    object_types[col] != object_type]

        # these types do not provide any insight
        new_list = ['weight', 'sample', 'coin-weight']
        for element in new_list:
            for col in object_types.columns:
                object_types.loc[object_types[col] == element, col] = None

        self.data = object_types.join(self.data, how="inner")
        self.data.drop(columns=['Object type'], inplace=True)

    def __clean_materials(self):

        materials = self.data['Materials'].str.split("; ")
        materials.columns = ['material_type1', 'material_type2',
                             'material_type3']

        # only the first 3 columns are useful
        materials = materials.loc[:, :2]

        self.data = self.data.join(materials, how='inner')
        self.data.drop(columns="Materials")

    def to_excel(self):
        with pd.ExcelWriter(os.path.join(self.path, self.file_name)) as writer:
            self.data.to_excel(writer, index=False)


def clean_denominator(df: pd.DataFrame) -> pd.DataFrame:
    denominators = df['Denomination'].str.split("; ", expand=True)

    denominators.dropna(how="all", inplace=True)

    denominators = denominators[~denominators[0].str.contains("\?")]

    # these are actually materials, not denominations
    actually_materials = ['potin']

    # left join at the end to maintain NaNs
