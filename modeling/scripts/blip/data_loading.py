from torch.utils.data import Dataset, DataLoader, random_split
from datasets import load_dataset
import torch

class HnMDataset(Dataset):
    def __init__(self, dataset, processor):
        self.dataset = dataset
        self.processor = processor

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        encoding = self.processor(images=item["image"], text=item["text"], padding="max_length", return_tensors="pt")
        # remove batch dimension
        encoding = {k:v.squeeze() for k,v in encoding.items()}
        return encoding

def prepare_data(dataset, data_processor, train_size, batch_size):
    # create dataset
    ds = load_dataset(dataset, split='train')
    dataset = HnMDataset(ds, data_processor)
    
    # train/val split
    train_set, val_set = random_split(dataset, lengths=[train_size, 1-train_size], generator=torch.Generator().manual_seed(42))

    # data loader
    train_loader = DataLoader(train_set, shuffle=True, batch_size=batch_size)
    val_loader = DataLoader(val_set, shuffle=False, batch_size=2 * batch_size)

    return train_loader, val_loader