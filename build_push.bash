# Workflow:
# - While developing, track changes in release_notes.md
# - Update README.md
# - Update the version number in pyproject.toml
# - run this script with the appropriate version number as the first parameter
# - Create a GitHub Release according to the template of a previous one, paste the release_notes.md contents and link to the new pypi release page.
# - Clear release_notes.py and commit to start the development of the next version

python3 -m build
python3 -m twine upload "dist/el_std_py-$1*"