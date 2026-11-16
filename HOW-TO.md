# GitHub profile: setup (about 10 minutes)

1. On GitHub, create a **public** repo named exactly `Taver-Versch` (same as your username). GitHub shows
   its README on your profile.
2. Upload `README.md`, the `assets` folder and the `.github` folder (use GitHub Desktop or drag the folders in,
   so the hidden `.github` folder comes along). `make_header.py` and `fonts` can go up too,
   they're only needed to rebuild the header.
3. Go to the repo's **Actions** tab, pick **Generate snake**, and click **Run workflow**. When it's done, the
   coral snake shows up at the bottom of your profile, and it redraws itself every day.

## Changing the header
The terminal lines are at the top of `make_header.py` (`LINES`). Edit them, then run `python make_header.py` and upload the two new files in `assets/`.

The header's font is baked into the SVG, so it doesn't depend on any outside
service. Only the snake comes from a GitHub Action.
