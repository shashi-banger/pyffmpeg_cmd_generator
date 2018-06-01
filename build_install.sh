pip uninstall --exists-action w ffmpeg-cmd-gen
python setup.py bdist_wheel --universal
pip install dist/ffmpeg_cmd_gen-0.1-py2.py3-none-any.whl
