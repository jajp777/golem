import pickle
from abc import ABCMeta, abstractmethod

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import BATCH_SIZE, IRIS_SIZE, TEST_SIZE
from .utils import derandom


class BatchManager(metaclass=ABCMeta):

    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> (np.ndarray, np.ndarray):
        pass

    @abstractmethod
    def save(self, batch_num: int, filepath: str):
        pass

    @abstractmethod
    def get_input_size(self) -> int:
        pass

    @abstractmethod
    def get_full_training_set(self) -> (np.ndarray, np.ndarray):
        pass

    @abstractmethod
    def get_order_of_batches(self):
        pass


class IrisBatchManager(BatchManager):

    def __init__(self, datafile, derandom_seed=0):
        self.datafile = datafile

        data = pd.read_csv(datafile, header=None)

        derandom(derandom_seed)
        data = data.reindex(np.random.permutation(data.index))

        y = pd.get_dummies(data[8]).values
        x = data[list(range(7))]
        x = ((x - x.mean()) / (x.max() - x.min())).values

        derandom(derandom_seed)
        x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                            test_size=TEST_SIZE,
                                                            random_state=42)
        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.current_index = 0

        self.indexing = list(data.index)
        self.derandom_seed = derandom_seed

    def __iter__(self):
        return self

    def __next__(self):
        batch = (self.x_train[self.current_index: self.current_index + BATCH_SIZE],
                 self.y_train[self.current_index: self.current_index + BATCH_SIZE])

        self.current_index = (self.current_index + BATCH_SIZE) % IRIS_SIZE
        return batch

    def save(self, batch_num, filepath):
        print("aaaa", batch_num, self.current_index)
        # assert(batch_num == self.current_index) # TODO why it doesn't work?

        batch = (self.x_train[self.current_index: self.current_index + BATCH_SIZE],
                 self.y_train[self.current_index: self.current_index + BATCH_SIZE])

        with open(filepath, "wb") as f:
            pickle.dump(batch, f)

    def get_input_size(self):
        return self.x_train[0].size

    def get_full_training_set(self):
        return self.x_train, self.y_train

    def get_order_of_batches(self):
        return self.indexing
