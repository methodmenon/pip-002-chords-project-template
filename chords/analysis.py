from __future__ import division

import math

import numpy
import librosa
import scipy.spatial.distance
import scipy.signal

CHORDS = numpy.array([
    [1,0,0,0,1,0,0,1,0,0,0,0],
    [1,0,0,1,0,0,0,1,0,0,0,0],
    [0,1,0,0,0,1,0,0,1,0,0,0],
    [0,1,0,0,1,0,0,0,1,0,0,0],
    [0,0,1,0,0,0,1,0,0,1,0,0],
    [0,0,1,0,0,1,0,0,0,1,0,0],
    [0,0,0,1,0,0,0,1,0,0,1,0],
    [0,0,0,1,0,0,1,0,0,0,1,0],
    [0,0,0,0,1,0,0,0,1,0,0,1],
    [0,0,0,0,1,0,0,1,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0],
    [1,0,0,0,0,1,0,0,1,0,0,0],
    [0,1,0,0,0,0,1,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,1,0,0],
    [0,0,1,0,0,0,0,1,0,0,0,1],
    [0,0,1,0,0,0,0,1,0,0,1,0],
    [1,0,0,1,0,0,0,0,1,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,1],
    [0,1,0,0,1,0,0,0,0,1,0,0],
    [1,0,0,0,1,0,0,0,0,1,0,0],
    [0,0,1,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,1,0,0,0,0,1,0],
    [0,0,0,1,0,0,1,0,0,0,0,1],
    [0,0,1,0,0,0,1,0,0,0,0,1]
])

CHORD_NAMES = numpy.array([#"A", "Am",
               #"A#", "A#m",
               #"B", "Bm",
               "C", "Cm",
               "C#", "C#m",
               "D", "Dm",
               "D#", "D#m",
               "E", "Em",
               "F", "Fm",
               "F#", "F#m",
               "G", "Gm",
               "G#", "G#m",
               "A", "Am",
               "A#", "A#m",
               "B", "Bm"])

"""analyse funtion
Takes the path to a file as an argument
Returns a dictionary containing the results of the analysis
"""
def analyse(filename, resample_to=2756, bt_hop_length=128, chroma_hop_length=512, chroma_n_fft=1024):
  #load audiofile-> return as floating point time series (array) with a sampling rate (int>0)
  samples, sampleRate = librosa.load(filename)
  length = float(len(samples))/sampleRate
  if resample_to:
    #resample time series from sampleRate to resample_to rate
    samples = librosa.resample(samples, sampleRate, resample_to)
    sampleRate = resample_to
  newSampleRate = 2756
  #resample time series from sampleRate to newSampleRate(2756)
  samples = librosa.resample(samples, sampleRate, newSampleRate)
  sampleRate = newSampleRate
  #track the beats from the time series in samples, using the number of audio samples reps by hop_length
  # --> returning tempo(estimated global tempo in bpmin) and beats (frame numbers of estimated beat events)
  tempo, beats = librosa.beat.beat_track(samples, sampleRate, hop_length=bt_hop_length)
  #convert the frame counts in 'beats' to time (seconds)
  beat_times = librosa.frames_to_time(beats, sampleRate, hop_length=bt_hop_length)
  #draw a chromagram using the data from samples, sampleRate, hop_length, and window size specified by n_fft
  chromagram = librosa.feature.chromagram(samples, sampleRate, hop_length=chroma_hop_length, n_fft=chroma_n_fft)
  #permute the dimensions of chromogram into a new array
  chromagram = numpy.transpose(chromagram)
  #compute the cosine distance between chromogram and CHORDS
  distances = scipy.spatial.distance.cdist(chromagram, CHORDS, "cosine")
  #return the indices of the minimum values along axis=1 (axis=0 reps the columns, axis=1 reps the rows)
  chords = distances.argmin(axis=1)
  #apply median filter to chords, the size of the median filter is rep by the kernal of size 11
  chords = scipy.signal.medfilt(chords, 11)
  #create a new array from th chords array using points where the discrete difference along the x-axis is not 0
  chord_frames = numpy.array(numpy.where(numpy.diff(chords) != 0))
  chords = chords[chord_frames][0].astype(int)
  #convert the frame counts in 'chord_frames' to time(seconds) 
  chord_times = librosa.frames_to_time(chord_frames, sampleRate, hop_length=chroma_hop_length, n_fft=chroma_n_fft)[0]
  chord_names = CHORD_NAMES[chords]

  return {"beats": list(beat_times),
          "chords": [{"chord": chord_name, "time": chord_time} for chord_name, chord_time in zip(chord_names, chord_times)],
          "tempo": tempo}