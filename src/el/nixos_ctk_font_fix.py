"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
18.07.25, 13:46
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

WARNING! Wild botch ahead!
Runtime changes the permissions of the Customtkinter
font files that CTk copies to ~/.fonts at every startup.
On NixOS these are copied from the store, and therefore have only
read permissions. On the next start, font loading fails because the fonts
couldn't be overwritten and CTk doesn't like that (even though it's not an issue).
So to fix this we just add write permissions to those files by importing
this module very early at application startup (before importing CTk).

This should probably fixed with a patch of customtkinter on nixpkgs but
is a dirty workaround for the time being.
"""

import os

fonts = [
    "Roboto-Regular.ttf",
    "Roboto-Medium.ttf",
    "CustomTkinter_shapes_font.otf",
]
base = os.path.expanduser("~/.fonts")

# make all the font files writable in case they exist
for font in fonts:
    path = os.path.join(base, font)
    if os.path.exists(path) and os.path.isfile(path):
        os.chmod(path, 0o664)