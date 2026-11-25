import kagglehub
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

dataset = "vedauv/what-makes-a-song-go-viral-10000-tracks/versions/1"
ruta_csv = kagglehub.dataset_download(dataset, path="viral_songs.csv")
df = pd.read_csv(ruta_csv)

print(df.shape)
df.head()