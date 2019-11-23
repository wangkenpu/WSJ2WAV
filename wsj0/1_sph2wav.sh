#!/bin/bash

# Copyright  2019  Microsoft (author: Ke Wang)

set -euo pipefail


stage=0

wsj0_dir=/mnt/data/WSJ/CSR-I-WSJ0-LDC93S6A
save_dir=/mnt/data/WSJ/WSJ0-WAV


if [ $stage -le 0 ]; then
  echo ">>> Convert sphere format to waveform ..."

  sph2pipe=tools/sph2pipe_v2.5/sph2pipe

  tmp=data/wsj0
  mkdir -p $tmp
  find $wsj0_dir -iname '*.wv*' | grep -e 'si_tr_s' -e 'si_dt_05' -e 'si_et_05' > $tmp/sph.list

  cat $tmp/sph.list | while read line; do
    wav=$(echo "$line" | sed "s:wv[12]:wav:g" | awk -v dir=$save_dir -F'/' '{printf("%s/%s/%s/%s", dir, $(NF-2), $(NF-1), $NF)}')
    echo $wav
    mkdir -p $(dirname $wav)
    $sph2pipe -f wav $line > $wav
  done > $tmp/wav.list
  echo ">>> Convert WSJ0 to Waveform Successfully."
fi
