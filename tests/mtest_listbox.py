"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
01.11.24, 17:03
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Manual test script for listbox
"""

import sys
sys.path.append("./src/")    # allows importing el when running like this: python tests/mtest_listbox.py

import uuid
import customtkinter as ctk
from PIL import Image
from el.widgets import CTkListbox, OptionEntry


if __name__ == "__main__":
    window = ctk.CTk()
    window.title("CTkListBox")
    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    listbox = CTkListbox[uuid.UUID](
        master=window,
        width=200,
        height=400,
        multiselect_mode="modifier"
    )
    listbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def print_sel_indices(indices: list[int]) -> None:
        print(f"indices: \n\t{"\n\t".join(str(i) for i in indices)}")
    listbox.selected_indices >> print_sel_indices
    
    def print_sel_indices(sel_data: uuid.UUID) -> None:
        print(f"users data: \n\t{"\n\t".join(f"{d}" for d in sel_data)}")
    listbox.selected_data >> print_sel_indices

    def set_options():
        listbox.set_options([
            OptionEntry(
                user_data=uuid.uuid4(),
                label="Hello0",
                icon=ctk.CTkImage(light_image=Image.open("/home/melektron/Documents/local_repos/hinstech/da_development/06_rf_eval_analyser/data/assets/arrows.png"))
            ),
            OptionEntry(
                user_data=uuid.uuid4(),
                label="Hello1",
                icon=ctk.CTkImage(light_image=Image.open("/home/melektron/Documents/local_repos/hinstech/da_development/06_rf_eval_analyser/data/assets/export.png"))
            ),
            OptionEntry(
                user_data=uuid.uuid4(),
                label="Hello2",
                disabled=True
            )
        ])
    btn_set_opts = ctk.CTkButton(window, text="Set options", command=set_options)
    btn_set_opts.grid(row=1, column=0)

    def add_options():
        prev_options = listbox.get_options()
        listbox.set_options(prev_options + [
            OptionEntry(
                user_data=uuid.uuid4(),
                label=f"Hello{len(prev_options)}",
                icon=ctk.CTkImage(light_image=Image.open("/home/melektron/Documents/local_repos/hinstech/da_development/06_rf_eval_analyser/data/assets/export.png"))
            ),
            OptionEntry(
                user_data=uuid.uuid4(),
                label=f"Hello{len(prev_options) + 1}"
            ),
            OptionEntry(
                user_data=uuid.uuid4(),
                label=f"Hello3{len(prev_options) + 2}",
                disabled=True,
                icon=ctk.CTkImage(light_image=Image.open("/home/melektron/Documents/local_repos/hinstech/da_development/06_rf_eval_analyser/data/assets/export.png"))
            )
        ])
    btn_add_opts = ctk.CTkButton(window, text="Add options", command=add_options)
    btn_add_opts.grid(row=2, column=0)

    def get_options():
        print(f"options: \n\t{"\n\t".join(f"{o}" for o in listbox.get_options())}")
    btn_get_opts = ctk.CTkButton(window, text="Get options", command=get_options)
    btn_get_opts.grid(row=3, column=0)
    
    window.mainloop()