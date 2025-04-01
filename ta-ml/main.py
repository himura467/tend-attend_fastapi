import matplotlib.pyplot as plt
import pandas as pd
import timesfm
import torch

tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend="gpu",
        horizon_len=24,
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        huggingface_repo_id="google/timesfm-1.0-200m-pytorch"
    ),
)

df = pd.read_csv(
    filepath_or_buffer="https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv",
    index_col="Month",
    parse_dates=True,
)
df = df[["Passengers"]]

context_length = 96
forecast_horizon = 24

train_data = df.iloc[-(context_length + forecast_horizon) : -forecast_horizon]
test_data = df.iloc[-forecast_horizon:]
train_tensor = torch.tensor(
    train_data["Passengers"].values, dtype=torch.float
).unsqueeze(0)
test_tensor = torch.tensor(test_data["Passengers"].values, dtype=torch.float).unsqueeze(
    0
)

frequency_input = [0] * train_tensor.size(1)
point_forecast, _ = tfm.forecast(train_tensor, freq=frequency_input)
forecast_tensor = torch.tensor(point_forecast)

plt.figure(figsize=(12, 6))
plt.plot(train_data.index, train_data["Passengers"], label="History", color="blue")
plt.plot(
    test_data.index,
    test_data["Passengers"],
    label="True",
    color="green",
    linestyle="--",
)
forecast_index = pd.date_range(
    start=test_data.index[0], periods=forecast_horizon, freq="ME"
)
plt.plot(
    forecast_index,
    forecast_tensor.numpy().flatten(),
    label="Forecast",
    color="red",
    linestyle="--",
)

plt.xlabel("Date")
plt.ylabel("Passengers")
plt.title("Airline Passengers Forecast")
plt.legend()
plt.show()
