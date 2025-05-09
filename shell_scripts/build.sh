pyinstaller \
    --onefile \
    --add-data ./data/config.json:./data/ \
    --add-data ./data/static/NotoColorEmoji.ttf:./data/static/ \
    main.py

# pyinstaller \
#     --onedir \
#     --add-data ./data/config.json:./data/ \
#     --add-data ./data/static/NotoColorEmoji.ttf:./data/static/ \
#     main.py
