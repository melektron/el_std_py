"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
28.08.25, 14:05
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Asset manager class to load and prepare image files.
"""

from ._deps import *

import typing
from pathlib import Path
import el.ctk_utils as ctku


class AssetManager:
    """
    The asset manager provides functions to easily load images to be used
    as UI assets in a scaling and color-theme/color aware manner.

    It is mainly intended for monochrome UI shapes for the time being,
    but functions for adding non-monochrome icons may be added.

    ## Monochrome Icons

    Monochrome icons should best be provided in PNG format with black as the 
    foreground and transparent (using alpha) everywhere else.
    For the recoloring to work, they must be of color_type 6 (RGBA) 
    8bpc, should however generally have a Bit depth of 1 for RGB and 8 Bit for Alpha.
    This indicates that the images only contain fully black/white pixels but with 
    varying transparency value, with the transparency layer acting as a mask defining the
    icon shape. If this is the case, black pixels can be easily recolored to anything without
    creating bleeding artifacts on anti-aliased edges.

    Check the color mode using ImageMagick's identify: 

    ```
    identify -verbose image.png
    ```

    It should contain something like this. The channel depth may vary if the image is not 
    a black+transparent mask.

    ```
    ... (unimportant stuff)

    Depth: 8-bit
    Channel depth:
        red: 1-bit
        green: 1-bit
        blue: 1-bit
        alpha: 8-bit

    ... (more unimportant stuff)

    Properties:
        date:create: 2024-10-19T18:47:19+00:00
        date:modify: 2024-10-19T18:47:19+00:00
        png:bKGD: chunk was found (see Background color, above)
        png:IHDR.bit-depth-orig: 8
        png:IHDR.bit_depth: 8
        png:IHDR.color-type-orig: 6
        png:IHDR.color_type: 6 (RGBA)                    <- this is important, should not be something like type 3
        png:IHDR.interlace_method: 0 (Not interlaced)
        png:IHDR.width,height: 512, 512
        png:pHYs: x_res=4137, y_res=4137, units=1
        png:sRGB: intent=0 (Perceptual Intent)
        png:tIME: 2024-10-19T18:47:19Z
        signature: d1dd0e1617e34b9b44b517dcc36f0f13d0192264c70a5aec930d60fec88dbac2

    ... (more unimportant stuff)
    ```

    Sometimes images from online sources can have an invalid color type (e.g. type 3) wich 
    can cause weird errors such as ```ValueError: buffer is not large enough``` when trying 
    to recolor them. In such cases, open the image with GIMP and re-export it to PNG with 
    the color mode `8bpc RGBA`.
    """

    def __init__(
        self, 
        base_path: Path | None = None,
        default_btn_icon_size: tuple[int, int] = (20, 20)
    ) -> None:
        """Creates an asset manager to load assets.

        All options may be accessed on the created instance
        and modified after creation, although changes only apply
        to assets loaded after the modification.

        Parameters
        ----------
        base_path : Path
            Directory to search for assets.
        default_btn_icon_size : tuple[int, int], optional
            Default size for button icons in pixels, by default 20x20
            which nicely fits the default CTk button height of 28.
            CTk widget scaling will be applied to this, so
            the actual size on screen may differ. 
        """
        self.base_path = base_path
        self.default_btn_icon_size = default_btn_icon_size

    def load_button_icon(
        self,
        owner: tk.Tk | tk.Widget,
        name: str,
        size: tuple[int, int] | None = None
    ) -> ctk.CTkImage:
        """
        Loads a monochrome button icon (see `AssetManager` doc for details) and
        recolors it to match the button text color according to the CTk color
        theme and appearance mode.

        Parameters
        ----------
        owner : tk.Tk | tk.Widget
            Widget to own the resulting CTkImage object
        name : str
            asset file name to load
        size : tuple[int, int] | None, optional
            Size of the image in pixels. If not passed,
            the default value of the respective `AssetManager` 
            will be used.

        Returns
        -------
        ctk.CTkImage
            Image object to be passed to CTkButton or another widget.
        """
        
        if size is None:
            size = self.default_btn_icon_size
        
        text_color: str | tuple[str, str] = ctku.homogenize_color_types(ctk.ThemeManager.theme["CTkButton"]["text_color"])

        base_img = Image.open(self.base_path / f"{name}")

        # recolor icon to match text color and resize
        image_data = np.asarray(base_img).copy()
        black_mask = (image_data[..., :3] == 0).all(axis=-1)

        image_data_light = image_data.copy()
        image_data_dark = image_data.copy()
        image_data_light[black_mask, :3] = ctku.tk_to_rgb8(ctku.apply_apm(text_color, "Light"), owner)
        image_data_dark[black_mask, :3] = ctku.tk_to_rgb8(ctku.apply_apm(text_color, "Dark"), owner)
        # light_img = Image.fromarray(np.zeros((48, 48, 3)), mode="RGB")
        light_img = Image.fromarray(image_data_light, mode="RGBA")
        dark_img = Image.fromarray(image_data_dark, mode="RGBA")

        return ctk.CTkImage(
            light_image=light_img,
            dark_image=dark_img,
            size=size
        )


    def load_colored_button_icon(
        self,
        owner: tk.Tk | tk.Widget, 
        name: str, 
        color: ctku.Color,
        size: tuple[int, int] | None = None
    ) -> ctk.CTkImage:
        """
        Loads a monochrome button icon (see `AssetManager` doc for details) and
        recolors it to the provided color. If the color is appearance mode aware,
        the resulting image will be as well.

        Parameters
        ----------
        owner : tk.Tk | tk.Widget
            Widget to own the resulting CTkImage object
        name : str
            asset file name to load
        color : ctku.Color
            color of the image foreground.
            Can be a tuple of colors for appearance
            mode awareness.
        size : tuple[int, int] | None, optional
            Size of the image in pixels. If not passed,
            the default value of the respective `AssetManager` 
            will be used.

        Returns
        -------
        ctk.CTkImage
            Image object to be passed to CTkButton or another widget.
        """

        if size is None:
            size = self.default_btn_icon_size
        
        base_img = Image.open(self.base_path / f"{name}")

        # recolor icon to match text color and resize
        image_data = np.asarray(base_img).copy()
        black_mask = (image_data[..., :3] == 0).all(axis=-1)

        image_data_light = image_data.copy()
        image_data_dark = image_data.copy()
        image_data_light[black_mask, :3] = ctku.tk_to_rgb8(ctku.apply_apm(color, "Light"), owner)
        image_data_dark[black_mask, :3] = ctku.tk_to_rgb8(ctku.apply_apm(color, "Dark"), owner)
        # light_img = Image.fromarray(np.zeros((48, 48, 3)), mode="RGB")
        light_img = Image.fromarray(image_data_light, mode="RGBA")
        dark_img = Image.fromarray(image_data_dark, mode="RGBA")

        return ctk.CTkImage(
            light_image=light_img,
            dark_image=dark_img,
            size=size
        )