python3 -m PyInstaller \
    --onefile \
    --add-data ./data/static/NotoColorEmoji.ttf:./data/static/ \
    main.py

# python3 -m PyInstaller \
#     --onedir \
#     --add-data ./data/static/NotoColorEmoji.ttf:./data/static/ \
#     main.py
