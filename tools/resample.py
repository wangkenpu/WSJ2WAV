#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Copyright  2019  Microsoft (author: Ke Wang)

from __future__ import absolute_import, division, print_function

import argparse
import librosa
import os
import re

import numpy as np
from scipy.io import wavfile
from tqdm import tqdm

MAX_INT16 = np.iinfo(np.int16).max

def main():
    wav_list = get_wav(args.input_dir)
    for idx in tqdm(range(len(wav_list))):
        item = wav_list[idx]
        name = os.path.splitext(os.path.basename(item))[0] + '.wav'
        save_path = os.path.join(args.save_dir, name)
        wav = wav_read(os.path.join(args.input_dir, item), args.sample_rate)
        wavwrite(wav, args.sample_rate, save_path)
    print('>>> Resample waveform to {:d}k done.'.format(
        int(args.sample_rate / 1000)))


def get_wav(input_dir):
    filename = [i for i in os.listdir(input_dir)]
    filtered = [i for i in filename if re.match(r'.+\.wav', i)]
    return filtered


def wav_read(path, sample_rate):
    audio = librosa.load(path, sr=sample_rate, dtype=np.float32)[0]
    return audio


def wavwrite(signal, sample_rate, path):
    signal = (signal * MAX_INT16).astype(np.int16)
    wavfile.write(path, sample_rate, signal)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', '-i', type=str, required=True,
        help='input wave directory')
    parser.add_argument('--save-dir', '-o', type=str, required=True,
        help='output wave directory')
    parser.add_argument('--sample-rate', '-sr', type=int, default=16000,
        help='resample rate (default: 16000)')
    args = parser.parse_args()
    os.makedirs(args.save_dir, exist_ok=True)
    main()
