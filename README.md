# WSJ Data Preparation

This repository aims at providing some useful scritps to do data preparation for WSJ data.

## Install Necessary Tools

```bash
cd tools
make
```

## How to Use

### WSJ0

```bash
# convert sphere to waveform
bash wsj0/1_sph2wav.sh   # remember to change wsj0_dir and save_dir

# add noise
python wsj0/2_prep_noisy_data.py -h
```

## Public Dataset

There are some public datasets we can use, including noise, RIR and well-simulated noisy speech.

### Noise Datasets

You can use any noise corpus. But the sample rate of noise and clean speech must be same. Ohterwise, you need to use `tools/resample.py` to down-sample clean speech or noise. There are some open source noise we can use:

1. [Nonspeech100](http://web.cse.ohio-state.edu/~wang.77/pnl/corpus/HuNonspeech/HuCorpus.html)
2. [MUSAN](http://www.openslr.org/17/)
3. [freesound](https://freesound.org/browse/)

### Room Impulse Response (RIR)

1. [OpenSLR](http://www.openslr.org/28/)
2. [AcouSP](http://www.dreams-itn.eu/index.php/dissemination/science-blogs/24-rir-databases)

### Noisy Speech Datasets

1. [SUPERSEDED](https://datashare.is.ed.ac.uk/handle/10283/1942)
