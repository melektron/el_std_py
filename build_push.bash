# Workflow:
# - While developing, track changes in release_notes.md
# - Update README.md
# - Update the version number in pyproject.toml
# - Create a preparation commit
# - run this script with the appropriate version number as the first parameter
# - Create a GitHub Release according to the template of a previous one, paste the release_notes.md contents and link to the new pypi release page.
# - Clear release_notes.py and commit to start the development of the next version

# Note: Twine > 6.0.1 has a problem with uploading. It doesn't properly recognize the license.
# To fix this, install twine==6.0.0 and everything works as expected. Hopefully this will be fixed soon.
# https://stackoverflow.com/questions/79408101/what-is-the-correct-way-of-specifying-the-license-in-pyproject-toml-file-for-a-n
python3 -m build
python3 -m twine upload "dist/el_std_py-$1*"