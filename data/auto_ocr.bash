for f in *; do
    # mv -- "$f" "${f#*ล\.}";
    # mv -- "$f" "${f%% *}";
    # mv -- "$f" "64_3_${f}";
    python ../../ocrAndSave.py -i "$f" -o "$f".txt
done