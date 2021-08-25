import os

import pandas as pd


class BritishMuseum:

    def __init__(self, path="/Users/fabian/Cozy Drive/Coin Project/rohdaten"):
        self.path = path
        self.file_name = "megred_data.xlsx"
        self.__data = pd.DataFrame()
        self.__load_data()
        self.__clean_up_data()

    def __load_data(self) -> None:
        for file in os.listdir(self.path):
            if file.endswith(".csv"):
                file_path = os.path.join(self.path, file)
                df = pd.read_csv(file_path)
                self.__data = self.__data.append(df, ignore_index=True)

        self.__data.drop_duplicates(subset="Museum number", inplace=True)

    def __drop_empty_cols(self) -> None:
        empty_cols = []
        for col in self.__data.columns:
            if self.__data[col].isna().all():
                empty_cols.append(col)

        self.__data.drop(columns=empty_cols, inplace=True)

    def __clean_object_types(self) -> None:
        object_types = self.__data['Object type'].str.split("; ", expand=True)

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

        self.__data = object_types.join(self.__data, how="inner")
        self.__data.drop(columns=['Object type'], inplace=True)

    def __clean_denominator(self) -> None:
        """
        For the start we only want to consider denominator with more than 75
        coins in sample size. This drops 300+ Denominators while only losing
        about 3000 coins from the sample

        :return:
        """
        coin_count = self.__data.groupby(["Denomination", "Materials"])
        coin_count = coin_count['Museum number'].count()
        coin_count = coin_count.reset_index()

        denominator = coin_count.loc[
            coin_count['Museum number'] >= 75, 'Denomination'].unique()
        materials = coin_count.loc[
            coin_count['Museum number'] >= 75, 'Materials'].unique()

        na_values = self.__data.loc[self.__data['Denomination'].isna(), :]

        df = self.__data.loc[(self.__data['Denomination'].isin(denominator)) &
                             (self.__data['Materials'].isin(materials)), :]

        self.__data = df.append(na_values)

    def __clean_find_spot(self) -> None:
        find_spots = self.__data.groupby("Find spot")['Museum number'].count()
        find_spots = find_spots.reset_index()

        # Extracting only the Name of the find spot and dropping all additional
        #   notes
        spots = find_spots['Find spot'].str.split(": ", expand=True)
        spots = spots[1].str.extract(r"([\w -]+)")
        spots.columns = ['find_spot_simplified']

        find_spots = pd.merge(spots, find_spots, left_index=True,
                              right_index=True)

        # excluding all acquired coins
        find_spots = find_spots.loc[
            ~find_spots['Find spot'].str.startswith("Found")]

        na_values = self.__data.loc[self.__data['Find spot'].isna()]
        df = pd.merge(self.__data, find_spots, left_on="Find spot",
                      right_on="Find spot", how="inner")
        self.__data = df.append(na_values)
        self.__data.drop(columns=['Museum number_y', 'Museum number'],
                         inplace=True)

        self.__data.rename(columns={'Museum number_x': 'Museum number'},
                           inplace=True)

    def __clean_up_data(self) -> None:
        """
        Calls all the clean up functions to prepare the data for DB import
        :return:
        """
        self.__clean_object_types()
        self.__clean_denominator()
        self.__clean_find_spot()

        self.__drop_empty_cols()

    def to_excel(self) -> None:
        with pd.ExcelWriter(os.path.join(self.path, self.file_name)) as writer:
            self.__data.to_excel(writer, index=False)

    def get_located_coins(self):
        """
        Returns all coins with a known find spot

        """

        return self.__data.loc[self.__data['find_spot_simplified'].notna(), :]

    def get_data(self):
        """Returns all data"""
        return self.__data