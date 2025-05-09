pyinstaller \
    --onefile \
    --add-data ./data/static/NotoColorEmoji.ttf:./data/static/ \
    main.py

# pyinstaller \
#     --onedir \
#     --add-data ./data/static/NotoColorEmoji.ttf:./data/static/ \
#     main.py
