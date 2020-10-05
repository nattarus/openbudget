for f in *; do
    # mv -- "$f" "${f#*ล\.}";
    # mv -- "$f" "${f%% *}";
    mv -- "$f" "${f}.pdf";
done