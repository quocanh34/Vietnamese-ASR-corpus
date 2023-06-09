import datasets
import pandas as pd
import numpy as np
from datasets import load_dataset, concatenate_datasets
from collections import Counter


class Deduplicate:
    def __init__(self, dataset):
        # dict with 'key' : index of sample in dataset, 'value' : sum of audio array
        self.dataset = dataset
        # cut_idx : list index of sample that is duplicated
        self.my_dict = self.create_dict()
        self.cut_idx, self.keep_idx = self.duplicated_index()

    def create_dict(self):
        freq_sum = self.dataset['sum']
        idx = list(range(len(freq_sum)))
        return dict(zip(idx, freq_sum))

    def duplicated_index(self):
        counts = Counter(self.my_dict.values())
        cut_idx = [k for k, v in self.my_dict.items() if counts[v] > 1]
        keep_idx = [k for k, v in self.my_dict.items() if counts[v] == 1]
        return cut_idx, keep_idx

    def create_potential_duplicate(self):
        dup_ds = self.dataset.select(self.cut_idx)
        undup_ds = self.dataset.select(self.keep_idx)
        return dup_ds, undup_ds

    def cut_duplicated_sample(self, dup_ds):
        test_ds = dup_ds.remove_columns(["audio", "transcription", "WER"])
        df = pd.DataFrame(test_ds)
        check = list(df.duplicated(subset=['w2v2_transcription', 'sum']))
        print("created check list...")
        indices = [index for (index, item) in enumerate(
            check) if item == False]
        print("get indices finished...")
        updated_undup_ds = dup_ds.select(indices)
        return updated_undup_ds

    def run_deduplicate(self):
        print(f"Before deduplicate : {self.dataset.num_rows} samples")
        # dup_ds : dataset contain example is duplicated in 'sum'
        print(
            f"There are {len(self.cut_idx)} duplicated in audio array sum...")
        dup_ds, undup_ds = self.create_potential_duplicate()
        print("Split dataset into duplicate and unduplicate complete...")
        print("Duplicated ds\n", dup_ds, "Keep ds\n", undup_ds)
        updated_undup_ds = self.cut_duplicated_sample(dup_ds)
        print("deduplicate finished...")
        print(updated_undup_ds)
        deduplicated_ds = concatenate_datasets([undup_ds, updated_undup_ds])
        print(deduplicated_ds)
        print(f"After deduplicate : {deduplicated_ds.num_rows} samples")
        return deduplicated_ds
