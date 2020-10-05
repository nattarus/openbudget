for f in *; do
    # mv -- "$f" "${f#*ล\.}";
    # mv -- "$f" "${f%% *}";
    mv -- "$f" "64_3_${f}";
done