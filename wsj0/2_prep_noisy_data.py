#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Copyright  2019  Microsoft (author: Ke Wang)

from __future__ import absolute_import, division, print_function

import argparse
import glob
import os
import sys

import numpy as np
import soundfile as sf
from scipy.io import wavfile
from tqdm import tqdm


EPS = np.finfo(np.float).eps
MAX_INT16 = np.iinfo(np.int16).max
SAMPLE_RATE = 16000

def read_wav(path):
    wav, sample_rate = sf.read(path, dtype='float32')
    if sample_rate != SAMPLE_RATE:
        raise RuntimeError('Expected sample rate is {}, but the sample rate '
            'of {} is {}'.format(SAMPLE_RATE, path, sample_rate))
    return wav, sample_rate


def save_wav(wav, path):
    wav = (wav * MAX_INT16).astype(np.int16)
    wavfile.write(path, SAMPLE_RATE, wav)


def sample_noise(noise, required_length):
    r"""Sample a noise segment"""
    required_length = int(required_length)
    n_sample, n_channel = noise.shape

    if n_sample <= required_length:
        n_extra = required_length - n_sample
        start = np.random.randint(low=0, high=n_extra)
        noise_sampled = np.zeros((required_length, n_channel))
        noise_sampled[start : start + n_sample, :] = noise
    else:
        n_extra = n_sample - required_length
        start = np.random.randint(low=0, high=n_extra)
        noise_sampled = noise[start: start + required_length, :]
    return noise_sampled


def repeat_noise(noise, required_length):
    r"""Random sample a noise of required length."""
    required_length = int(required_length)
    n_sample, n_channel = noise.shape

    if n_sample < required_length:
        repeat_times = int(np.ceil(required_length / n_sample))
        noise = np.tile(noise, (repeat_times, 1))
        n_sample = noise.shape[0]

    if n_sample == required_length:
        start = 0
    else:
        start = np.random.randint(low=0, high=n_sample-required_length)
    noise_repeated = noise[start : start + required_length, :]
    return noise_repeated


def compute_weight(clean, noise, snr):
    clean_power = np.mean(np.power(clean, 2.0))
    noise_power = np.mean(np.power(noise, 2.0))
    scale = np.sqrt(
        (10.0 ** (-snr / 10.0)) * clean_power / (noise_power + EPS))
    return scale


def add_noise(clean_path, noise_path, snr, scheme='repeat_noise'):
    r"""Add addtive noise to signal.

    Args:
        clean_path: path of clean wave
        noise_path: path of noisy wave
        snr: signal to noise ratio
        scheme: specify how to position the noise in the final waveform
    Return:
        distorted: distorted signal waveform
        save_name: save name of distorted waveform
    """
    clean, clean_fs = read_wav(clean_path)
    noise, noise_fs = read_wav(noise_path)
    clean_name = os.path.splitext(os.path.basename(clean_path))[0]
    noise_name = os.path.splitext(os.path.basename(noise_path))[0]
    save_name = '{}_{}_{:02.2f}.wav'.format(clean_name, noise_name, snr)

    clean = clean.reshape((-1, 1)) if clean.ndim == 1 else clean
    noise = noise.reshape((-1, 1)) if noise.ndim == 1 else noise
    n_sample, n_channel = clean.shape
    if clean_fs != noise_fs:
        raise RuntimeError('The sample rate of {}: {} is not equal to the '
                           'sample rate of {}: {}'.format(
                               clean_path, clean_fs, noise_path, noise_fs))

    scale = compute_weight(clean, noise, snr)
    noise_scaled = noise * scale
    if scheme == 'repeat_noise':
        noise_scaled = repeat_noise(noise_scaled, n_sample)
    elif scheme == 'sample_noise':
        noise_scaled = sample_noise(noise_scaled, n_sample)
    else:
        raise Exception('Unknown noise position scheme: {}'.format(scheme))
    distorted = clean + noise_scaled
    return distorted, save_name


def parse_dir(data_dir, dir_depth):
    file_list = []
    if dir_depth == 2:
        wav_fn_list = glob.glob(os.path.join(data_dir, '*', '*.wav'))
    elif dir_depth == 1:
        wav_fn_list = glob.glob(os.path.join(data_dir, '*.wav'))
    else:
        raise ValueError('Unsupported depth: {}'.format(dir_depth))
    return wav_fn_list


def main():
    clean_fn_list = parse_dir(args.clean_dir, args.clean_dir_depth)
    noise_fn_list = parse_dir(args.noise_dir, args.noise_dir_depth)
    noise_num = len(noise_fn_list)
    for idx in tqdm(range(len(clean_fn_list))):
        snr = np.random.uniform(low=args.snr_range[0], high=args.snr_range[1])
        noise_idx = np.random.randint(low=0, high=noise_num)
        distorted, save_name = add_noise(
            clean_fn_list[idx], noise_fn_list[noise_idx], snr, args.scheme)
        save_path = os.path.join(args.save_dir, save_name)
        save_wav(distorted, save_path)
    print('>>> Add noise done and the SNR range is from {}dB to {}dB.'.format(
        args.snr_range[0], args.snr_range[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add Noise")
    parser.add_argument('--clean-dir', '-cd', type=str, required=True,
        help='clean waveform directory')
    parser.add_argument('--clean-dir-depth', '-cdd', type=int, default=2,
        help='depth of clean waveform directory (default: 2)')
    parser.add_argument('--noise-dir', '-nd', type=str, required=True,
        help='clean waveform directory')
    parser.add_argument('--noise-dir-depth', '-ndd', type=int, default=1,
        help='clean waveform directory (default: 1)')
    parser.add_argument('--save-dir', '-sd', type=str, required=True,
        help='save directory')
    parser.add_argument('--seed', type=int, default=0,
        help='random seed (defautl: 0)')
    parser.add_argument('--snr-range', '-snr', type=float, default=[-5, 20],
        nargs=2, help='SNR range (default: -5 20)')
    parser.add_argument('--scheme', '-sc', type=str, default='repeat_noise',
        choices=['repeat_noise', 'sample_noise'],
        help='noise position scheme (default: repeat_noise)')
    args = parser.parse_args()
    os.makedirs(args.save_dir, exist_ok=True)
    np.random.seed(args.seed)
    main()
