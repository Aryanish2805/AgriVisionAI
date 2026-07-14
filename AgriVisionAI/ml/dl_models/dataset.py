import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class CropDataset(Dataset):
    def __init__(self, csv_file=None, dataframe=None, scaler=None, is_train=True, noise_level=0.0):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            dataframe (pd.DataFrame): Dataframe with annotations.
            scaler (StandardScaler): Scikit-Learn scaler object for normalizing features.
            is_train (bool): Indicates if this is the training set (to fit the scaler).
            noise_level (float): Standard deviation of Gaussian noise to add to scaled features.
        """
        if dataframe is not None:
            self.data_frame = dataframe.copy()
        elif csv_file is not None:
            self.data_frame = pd.read_csv(csv_file)
        else:
            raise ValueError("Either csv_file or dataframe must be provided")
        
        # We need N, P, K, temperature, humidity, ph, rainfall
        # Assuming original kaggle dataset columns or similar. We'll try to match N, P, K or nitrogen, phosphorus, potassium
        cols = self.data_frame.columns
        if 'N' in cols:
            feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        else:
            feature_cols = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
            
        label_col = 'label' if 'label' in cols else 'crop'
        self.data_frame = self.data_frame.dropna(subset=[label_col])
        self.features = self.data_frame[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values.astype(np.float32)
        
        if is_train:
            self.scaler = StandardScaler()
            self.features = self.scaler.fit_transform(self.features)
        else:
            self.scaler = scaler
            if self.scaler is not None:
                self.features = self.scaler.transform(self.features)
                
        # Inject Gaussian Noise to simulate real-world sensor inaccuracies
        if noise_level > 0.0:
            noise = np.random.normal(0, noise_level, self.features.shape).astype(np.float32)
            self.features += noise
            
        # Labels are strings, we need to map them to integers
        label_col = 'label' if 'label' in cols else 'crop'
        self.labels_str = self.data_frame[label_col].values
        self.classes = np.unique(self.labels_str)
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        self.labels = np.array([self.class_to_idx[label] for label in self.labels_str], dtype=np.int64)

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        features = self.features[idx]
        label = self.labels[idx]

        return torch.tensor(features), torch.tensor(label)

    def get_num_classes(self):
        return len(self.classes)
    
    def get_num_features(self):
        return self.features.shape[1]
