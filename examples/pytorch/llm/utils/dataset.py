from typing import Optional, Tuple

import numpy as np
from datasets import Dataset as HfDataset
from datasets import concatenate_datasets
from numpy.random import RandomState

from modelscope import MsDataset


def _processing_alpaca(dataset: HfDataset) -> HfDataset:
    instruction = dataset['instruction']
    input_ = dataset['input']
    res = []
    for inst, inp in zip(instruction, input_):
        if inp is not None and inp != '':
            if inp.startswith('输入：'):
                inp = inp[3:]
            inst = f'{inst}\n{inp}'
        res.append(inst)
    dataset = HfDataset.from_dict({
        'instruction': res,
        'output': dataset['output']
    })
    return dataset


def get_alpaca_en_dataset() -> HfDataset:
    dataset_en: HfDataset = MsDataset.load(
        'AI-ModelScope/alpaca-gpt4-data-en', split='train').to_hf_dataset()
    dataset_en = dataset_en.remove_columns(['text'])
    return _processing_alpaca(dataset_en)


def get_alpaca_zh_dataset() -> HfDataset:
    dataset_zh: HfDataset = MsDataset.load(
        'AI-ModelScope/alpaca-gpt4-data-zh', split='train').to_hf_dataset()
    return _processing_alpaca(dataset_zh)


def get_seed(random_state: RandomState) -> int:
    seed_max = np.iinfo(np.int32).max
    seed = random_state.randint(0, seed_max)
    return seed


def process_dataset(dataset: HfDataset, dataset_test_size: float,
                    dataset_sample: Optional[int],
                    dataset_seed: int) -> Tuple[HfDataset, HfDataset]:
    random_state = np.random.RandomState(dataset_seed)
    if dataset_sample is not None:
        index = random_state.permutation(len(dataset))[:dataset_sample]
        dataset = dataset.select(index)
    dataset = dataset.train_test_split(
        dataset_test_size, seed=get_seed(random_state))
    return dataset['train'], dataset['test']


DATASET_MAPPER = {
    'alpaca-en': get_alpaca_en_dataset,
    'alpaca-zh': get_alpaca_zh_dataset,
}


def get_dataset(dataset_names: str) -> HfDataset:
    dataset_name_list = dataset_names.split(',')
    dataset_list = []
    for dataset_name in dataset_name_list:
        get_function = DATASET_MAPPER[dataset_name]
        dataset_list.append(get_function())
    dataset = concatenate_datasets(dataset_list)
    return dataset
