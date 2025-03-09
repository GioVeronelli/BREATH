import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import math
import variables as v
from scipy.signal import butter, filtfilt, find_peaks

def load_data(xls_file):
    """
    Load data from an Excel file and return a DataFrame.
    """
    df = pd.read_excel(xls_file)
    return df

def plot_data(df):
    """
    # Plot the data in the DataFrame.
    """
    plt.plot(df.index, df['accZ'])
    plt.xlabel('Index')
    plt.ylabel('accZ')
    plt.show()

def remove_dc_offset(df):
    """
    Remove the DC offset from the data in the DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.

    Returns:
    pandas.DataFrame: The DataFrame with the DC offset removed.
    """
    df['accZ'] -= df['accZ'].mean()
    return df

def fourier_transform(df, Fs, nyq):
    """
    Perform the Fourier transform on the data in the DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame containing the signal data.
    Fs (float): The sampling frequency of the signal.
    nyq (float): The Nyquist frequency, which is half of the sampling frequency.

    Returns:
    tuple: A tuple containing the normalized frequencies and normalized magnitudes of the Fourier transform.
    """
    # Perform Fourier transform

    # Extract signal data from DataFrame 
    signal = df['accZ'].values

    # Apply a window function
    window = np.hanning(len(signal))
    signal_windowed = signal * window

    # Apply Fourier transform
    fourier_transform = np.fft.fft(signal_windowed)
    frequencies = np.fft.fftfreq(len(signal), d=1/Fs)

    # Normalize the frequency by the Nyquist frequency
    normalized_frequencies = frequencies / nyq

    # Normalize the amplitude by the number of samples
    normalized_magnitude = np.abs(fourier_transform) / len(signal)

    return normalized_frequencies, normalized_magnitude

# def fourier_transform_log(df, Fs, nyq):
#     """
#     Perform a logarithmic Fourier transform on the data in the DataFrame.
    
#     Parameters:
#     - df: pandas DataFrame containing the signal data
#     - Fs: Sampling rate in Hz
#     - nyq: Nyquist frequency in Hz
    
#     Returns:
#     - normalized_frequencies: Frequencies normalized by the Nyquist frequency
#     - log_magnitude: Logarithmic magnitudes of the Fourier transform
#     """
#     # Extract signal data from DataFrame and remove DC offset
#     signal = df['accZ'].values - np.mean(df['accZ'].values)

#     # Apply a window function
#     window = np.hanning(len(signal))
#     signal_windowed = signal * window

#     # Apply Fourier transform
#     fourier_transform = np.fft.fft(signal_windowed)
#     frequencies = np.fft.fftfreq(len(signal), d=1/Fs)

#     # Normalize the frequency by the Nyquist frequency
#     normalized_frequencies = frequencies / nyq

#     # Normalize the amplitude by the number of samples
#     normalized_magnitude = np.abs(fourier_transform) / len(signal)

#     # Convert magnitude to logarithmic scale
#     log_magnitude = 20 * np.log10(normalized_magnitude)

#     return normalized_frequencies, log_magnitude

def apply_filter(signal, low_freq, high_freq, nyq, order):
    """
    Apply a bandpass filter to the input signal.

    Parameters:
    signal (array-like): The input signal to be filtered.
    low_freq (float): The lower cutoff frequency of the bandpass filter.
    high_freq (float): The upper cutoff frequency of the bandpass filter.
    fs (float): The sampling frequency of the input signal from variables.py.
    order (int, optional): The order of the filter. Defaults to 1.

    Returns:
    array-like: The filtered signal.

    """
    low = low_freq / nyq
    high = high_freq / nyq
    b, a = butter(order, [low, high], btype='band')
    filtered_signal = filtfilt(b, a, signal)
    
    return filtered_signal

def find_peaks_and_lows(signal, threshold=0.01):
    """
    Find the peaks in a signal.

    Parameters:
    signal (array-like): The input signal.
    threshold (float, optional): The threshold for peak detection. Defaults to 0.01.

    Returns:
    array-like: The indices of the peaks in the signal.

    """
    peaks, _ = find_peaks(signal, height=threshold)
    lows, _ = find_peaks(-signal, height=threshold)
    
    return peaks, lows

def real_peaks(peaks, lows):
    """
    Find the real peaks in a signal by grouping adjacent peaks.

    Parameters:
    peaks (array-like): The indices of the peaks in the signal.
    lows (array-like): The indices of the lows in the signal.

    Returns:
    array-like: The indices of the real peaks in the signal.
    """
    final_peaks = []
    processed_peaks = set()

    # Consider each peak to see if it is part of a group of peaks
    for i in range(len(peaks)):
        if i in processed_peaks:
            continue

        current_group = [peaks[i]]
        processed_peaks.add(i)

        # Continue to search adjacent peaks until a low is spotted
        while i + 1 < len(peaks) and not any((lows > peaks[i]) & (lows < peaks[i + 1])):
            # if peaks[i + 1] - peaks[i] < 300:  # wait for 300 samples before considering a new peak
            current_group.append(peaks[i + 1])
            processed_peaks.add(i + 1)
            i += 1
            # else:
            #    break

        # Calculate the midpoint of the group of peaks once the group is complete
        if len(current_group) > 1:
            midpoint = int(np.round(np.mean(current_group)))
            final_peaks.append(midpoint)
        else:
            final_peaks.append(current_group[0])

    return np.array(final_peaks)

def real_lows(peaks, lows):
    """
    Find the real lows in a signal by grouping adjacent lows.

    Parameters:
    peaks (array-like): The indices of the peaks in the signal.
    lows (array-like): The indices of the lows in the signal.

    Returns:
    array-like: The indices of the real lows in the signal.
    """
    final_lows = []
    processed_lows = set()

    # Consideriamo ogni valle per vedere se deve essere raggruppata
    for j in range(len(lows)):
        if j in processed_lows:
            continue

        current_group = [lows[j]]
        processed_lows.add(j)

        # Continua a cercare valli adiacenti fino a che non si incontra un picco
        while j + 1 < len(lows) and not any((peaks > lows[j]) & (peaks < lows[j + 1])):
            # if lows[j + 1] - lows[j] < 300:  # Una soglia arbitraria di vicinanza
            current_group.append(lows[j + 1])
            processed_lows.add(j + 1)
            j += 1
            # else:
            #    break

        # Calcola il punto medio solo se il gruppo ha più di un elemento
        if len(current_group) > 1:
            midpoint = int(np.round(np.mean(current_group)))
            final_lows.append(midpoint)
        else:
            final_lows.append(current_group[0])

    return np.array(final_lows)

def respiratory_rate(peaks, fs):
    """
    Calculate the respiratory rate from the peak indices.

    Parameters:
    peaks (array-like): The indices of the peaks in the signal.
    fs (float): The sampling frequency of the signal.

    Returns:
    float: The respiratory rate in breaths per minute.

    """

    # Calculate the time between peaks
    time_diff = np.diff(peaks) / fs

    # Calculate the average time between peaks
    avg_time_diff = np.mean(time_diff)

    # Calculate the respiratory rate in breaths per minute
    respiratory_rate = 60 / avg_time_diff
    
    return respiratory_rate

def inspiratory_expiratory_time(peaks, lows, fs):
    """
    Calculate the inspiratory and expiratory times from the peak and low indices.

    Parameters:
    peaks (array-like): The indices of the peaks in the signal.
    lows (array-like): The indices of the lows in the signal.
    fs (float): The sampling frequency of the signal.

    Returns:
    float: The inspiratory time in seconds.
    float: The expiratory time in seconds.

    """
    # Calculate the time between peaks and subsequent lows
    inspiratory_times = []
    expiratory_times = []

    for i in range(min(len(peaks), len(lows)) - 1):
        # Find the next low after each peak
        if lows[i] > peaks[i]:
            inspiratory_times.append((lows[i] - peaks[i]) / fs)
            expiratory_times.append((peaks[i + 1] - lows[i]) / fs)

    # Calculate the average inspiratory and expiratory times
    avg_inspiratory_time = np.mean(inspiratory_times) if inspiratory_times else 0
    avg_expiratory_time = np.mean(expiratory_times) if expiratory_times else 0

    # Calculate the inspiratory to expiratory ratio (IER)
    if avg_expiratory_time != 0:
        ier = avg_inspiratory_time / avg_expiratory_time
    else:
        ier = np.inf

    return avg_inspiratory_time, avg_expiratory_time, ier