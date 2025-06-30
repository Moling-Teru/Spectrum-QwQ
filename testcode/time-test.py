import librosa
def get_duration_librosa(file_path):
    audio_data, sample_rate = librosa.load(file_path)
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    return duration
print(get_duration_librosa('Breathe In.mp3'))